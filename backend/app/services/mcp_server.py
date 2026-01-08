from __future__ import annotations

from typing import Sequence
import asyncio
import sqlalchemy as sa
from fastapi import HTTPException
from sqlalchemy import func, select, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import MCPServer, User
from app.schemas import (
    MCPServerCreate,
    MCPServerRead,
    MCPServerUpdate,
    MCPToolInfo,
    MCPServerRuntime,
)
from app.utils import load_mcp_tools_from_servers, is_admin_user as is_admin


def _ilike(term: str) -> str:
    t = (term or "").strip()
    t = t.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{t}%"


def _tool_schema(tool) -> dict | None:
    args_schema = getattr(tool, "args_schema", None)
    if args_schema is not None:
        try:
            return args_schema.model_json_schema()
        except Exception:
            pass
    schema = getattr(tool, "schema", None) or getattr(tool, "input_schema", None)
    if isinstance(schema, dict):
        return schema
    return None


async def probe_mcp_server(
    server: MCPServer, *, timeout_sec: float = 3.0
) -> MCPServerRuntime:
    try:
        async with asyncio.timeout(timeout_sec):
            tools = await load_mcp_tools_from_servers([server])

        infos: list[MCPToolInfo] = []
        for t in tools:
            infos.append(
                MCPToolInfo(
                    name=getattr(t, "name", "unknown"),
                    description=getattr(t, "description", None),
                    input_schema=_tool_schema(t),
                )
            )
        return MCPServerRuntime(reachable=True, tools=infos)
    except Exception as e:
        return MCPServerRuntime(reachable=False, error=str(e), tools=[])


class MCPServerService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: MCPServerCreate, *, user: User) -> MCPServerRead:
        exists = await self.session.scalar(
            select(sa.literal(True)).where(
                func.lower(MCPServer.name) == data.name.lower(),
                MCPServer.owner_id == user.id,
            )
        )
        if exists:
            raise ValueError(f"이미 존재하는 MCP 서버 이름입니다: {data.name!r}")

        safe_config = data.config.model_dump(mode="json")
        server = MCPServer(
            name=data.name.strip(),
            description=(data.description or None),
            config=safe_config,
            is_public=bool(data.is_public),
            owner_id=user.id,
        )
        self.session.add(server)
        try:
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            raise ValueError("MCP 서버 생성 중 무결성 오류가 발생했습니다.") from e

        await self.session.refresh(server)
        return MCPServerRead.model_validate(server)

    async def get(self, server_id: int, *, user: User) -> MCPServerRead:
        server = await self.session.get(MCPServer, server_id)
        if not server:
            raise ValueError(f"존재하지 않는 MCP 서버 ID입니다: {server_id}")
        if not (server.is_public or server.owner_id == user.id or is_admin(user)):
            raise HTTPException(status_code=403, detail="접근 권한이 없습니다.")
        dto = MCPServerRead.model_validate(server)
        runtime = await probe_mcp_server(server)
        dto = dto.model_copy(update={"runtime": runtime})

        return dto

    async def get_by_name(self, name: str) -> MCPServerRead:
        server = await self.session.scalar(
            select(MCPServer).where(func.lower(MCPServer.name) == name.lower())
        )
        if not server:
            raise ValueError(f"존재하지 않는 MCP 서버 이름입니다: {name!r}")
        return MCPServerRead.model_validate(server)

    async def get_list(
        self,
        *,
        user: User,
        q: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> Sequence[MCPServerRead]:
        stmt = select(MCPServer).order_by(MCPServer.id.desc())
        if not is_admin(user):
            stmt = stmt.where(
                or_(MCPServer.is_public.is_(True), MCPServer.owner_id == user.id)
            )
        if q:
            pattern = _ilike(q)
            stmt = stmt.where(
                sa.or_(
                    MCPServer.name.ilike(pattern, escape="\\"),
                    MCPServer.description.ilike(pattern, escape="\\"),
                )
            )
        stmt = stmt.offset(max(0, offset)).limit(min(200, max(1, limit)))
        rows = (await self.session.scalars(stmt)).all()
        return [MCPServerRead.model_validate(r) for r in rows]

    async def update(
        self, server_id: int, data: MCPServerUpdate, *, user: User
    ) -> MCPServerRead:
        server = await self.session.get(MCPServer, server_id, with_for_update=True)
        if not server:
            raise ValueError(f"존재하지 않는 MCP 서버 ID입니다: {server_id}")
        if not (server.owner_id == user.id or is_admin(user)):
            raise HTTPException(status_code=403, detail="수정 권한이 없습니다.")

        if data.name is not None:
            new_name = data.name.strip()
            dup = await self.session.scalar(
                select(sa.literal(True)).where(
                    sa.and_(
                        func.lower(MCPServer.name) == new_name.lower(),
                        MCPServer.owner_id == server.owner_id,
                        MCPServer.id != server_id,
                    )
                )
            )
            if dup:
                raise ValueError(f"이미 존재하는 MCP 서버 이름입니다: {new_name!r}")
            server.name = new_name

        if data.description is not None:
            server.description = data.description or None

        if data.config is not None:
            server.config = data.config.model_dump(mode="json")

        if data.is_public is not None:
            server.is_public = data.is_public

        try:
            await self.session.commit()

        except IntegrityError as e:
            await self.session.rollback()
            raise ValueError("MCP 서버 수정 중 무결성 오류가 발생했습니다.") from e

        await self.session.refresh(server)
        return MCPServerRead.model_validate(server)

    async def delete(self, server_id: int, *, user: User) -> None:
        server = await self.session.get(MCPServer, server_id)
        if not server:
            return
        if not (server.owner_id == user.id or is_admin(user)):
            raise HTTPException(status_code=403, detail="삭제 권한이 없습니다.")
        await self.session.delete(server)
        try:
            await self.session.commit()

        except IntegrityError as e:
            await self.session.rollback()
            raise ValueError(
                "MCP 서버를 삭제할 수 없습니다. 연결된 리소스를 먼저 해제하세요."
            ) from e
