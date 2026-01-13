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
    """
    Why: ILIKE 검색을 위한 안전한 패턴을 생성합니다.

    Args:
        term: 검색어.

    Returns:
        str: 이스케이프 처리된 패턴 문자열.
    """
    t = (term or "").strip()
    t = t.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{t}%"


def _tool_schema(tool) -> dict | None:
    """
    Why: MCP 툴의 입력 스키마를 표준 dict로 추출합니다.

    Args:
        tool: MCP 툴 객체.

    Returns:
        dict | None: JSON 스키마 또는 None.
    """
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
    """
    Summary: MCP 서버 연결 가능 여부와 툴 목록을 탐지합니다.

    Contract:
        - 지정된 시간 내에 응답이 없으면 실패로 처리합니다.
        - 실패 시 reachable=False와 error 메시지를 반환합니다.

    Args:
        server: MCP 서버 엔티티.
        timeout_sec: 타임아웃(초).

    Returns:
        MCPServerRuntime: 연결 상태 및 툴 목록.

    Side Effects:
        - 외부 MCP 서버 호출
    """
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
    """
    Summary: MCP 서버 등록/조회/수정/삭제를 담당합니다.

    Contract:
        - 소유자/관리자만 수정·삭제 가능합니다.
        - 중복 이름은 ValueError로 처리합니다.

    Side Effects:
        - DB 레코드 생성/수정/삭제
        - 외부 MCP 서버 탐지(조회 시)
    """
    def __init__(self, session: AsyncSession):
        """
        Why: MCP 서버 관련 작업에 사용할 DB 세션을 주입합니다.

        Args:
            session: 비동기 SQLAlchemy 세션.
        """
        self.session = session

    async def create(self, data: MCPServerCreate, *, user: User) -> MCPServerRead:
        """
        Summary: 새 MCP 서버를 등록합니다.

        Contract:
            - 동일 사용자 내 중복 이름은 허용하지 않습니다.

        Args:
            data: MCP 서버 생성 요청 데이터.
            user: 요청 사용자.

        Returns:
            MCPServerRead: 생성된 MCP 서버 DTO.

        Raises:
            ValueError: 중복 이름 또는 무결성 오류.

        Side Effects:
            - DB 레코드 생성
        """
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
        """
        Summary: MCP 서버 상세 정보를 조회하고 런타임 상태를 붙입니다.

        Args:
            server_id: MCP 서버 ID.
            user: 요청 사용자.

        Returns:
            MCPServerRead: 서버 상세 + 런타임 상태.

        Raises:
            ValueError: 서버 미존재.
            HTTPException: 접근 권한 없음.

        Side Effects:
            - 외부 MCP 서버 연결 테스트
        """
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
        """
        Summary: 이름으로 MCP 서버를 조회합니다.

        Args:
            name: MCP 서버 이름.

        Returns:
            MCPServerRead: 서버 DTO.

        Raises:
            ValueError: 서버가 존재하지 않는 경우.
        """
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
        """
        Summary: 접근 가능한 MCP 서버 목록을 조회합니다.

        Contract:
            - 관리자는 전체, 일반 사용자는 공개/소유 서버만 조회합니다.

        Args:
            user: 요청 사용자.
            q: 이름/설명 검색어.
            offset: 시작 위치.
            limit: 최대 개수(1~200).

        Returns:
            Sequence[MCPServerRead]: 서버 DTO 목록.

        Side Effects:
            - DB 조회
        """
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
        """
        Summary: MCP 서버 정보를 수정합니다.

        Contract:
            - 소유자/관리자만 수정 가능합니다.
            - 이름 변경 시 동일 사용자 내 중복을 금지합니다.

        Args:
            server_id: 수정 대상 서버 ID.
            data: 수정 요청 데이터.
            user: 요청 사용자.

        Returns:
            MCPServerRead: 수정된 서버 DTO.

        Raises:
            ValueError: 서버 미존재/중복 이름/무결성 오류.
            HTTPException: 수정 권한 없음.

        Side Effects:
            - DB 레코드 업데이트
        """
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
        """
        Summary: MCP 서버를 삭제합니다.

        Contract:
            - 소유자/관리자만 삭제 가능합니다.
            - 참조 중인 경우 무결성 오류로 실패합니다.

        Args:
            server_id: 삭제 대상 서버 ID.
            user: 요청 사용자.

        Raises:
            HTTPException: 삭제 권한 없음.
            ValueError: 무결성 오류.

        Side Effects:
            - DB 레코드 삭제
        """
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
