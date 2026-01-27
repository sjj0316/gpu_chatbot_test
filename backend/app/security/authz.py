from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload, undefer
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import MCPServer, ModelApiKey, User
from app.utils import is_admin_user


async def get_model_key_authorized(
    session: AsyncSession, key_id: int, user: User
) -> ModelApiKey:
    """
    Why: ModelApiKey 접근을 중앙에서 통제해 BOLA를 차단합니다.
    """
    res = await session.execute(
        select(ModelApiKey)
        .options(
            selectinload(ModelApiKey.provider),
            selectinload(ModelApiKey.purpose),
        )
        .where(ModelApiKey.id == key_id)
    )
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model API key not found.",
        )
    if not (obj.is_public or obj.owner_id == user.id or is_admin_user(user)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Model API key access denied.",
        )
    res = await session.execute(
        select(ModelApiKey)
        .options(
            undefer(ModelApiKey.api_key),
            selectinload(ModelApiKey.provider),
            selectinload(ModelApiKey.purpose),
        )
        .where(ModelApiKey.id == key_id)
    )
    return res.scalar_one()


async def get_mcp_servers_authorized(
    session: AsyncSession, ids: list[int], user: User
) -> list[MCPServer]:
    """
    Why: MCPServer 접근을 중앙에서 통제해 BOLA를 차단합니다.
    """
    if not ids:
        return []
    if is_admin_user(user):
        stmt = select(MCPServer).where(MCPServer.id.in_(ids))
    else:
        stmt = select(MCPServer).where(
            MCPServer.id.in_(ids),
            (MCPServer.is_public.is_(True) | (MCPServer.owner_id == user.id)),
        )
    res = await session.execute(stmt)
    servers = list(res.scalars())
    requested = set(ids)
    found = {s.id for s in servers}
    if requested - found:
        # 존재성 노출을 줄이기 위해 기본 정책은 403으로 처리한다.
        # 필요 시 404로 위장하는 정책으로 변경 가능.
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="MCP server access denied.",
        )
    return servers


async def get_mcp_server_authorized(
    session: AsyncSession,
    server_id: int,
    user: User,
    *,
    require_owner: bool = False,
    allow_missing: bool = False,
) -> MCPServer | None:
    """
    Why: MCPServer 단건 접근을 중앙에서 통제해 인가 정책을 통일합니다.
    """
    res = await session.execute(select(MCPServer).where(MCPServer.id == server_id))
    server = res.scalar_one_or_none()
    if not server:
        if allow_missing:
            return None
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MCP server not found.",
        )
    if is_admin_user(user):
        return server
    if require_owner:
        if server.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="접근 권한이 없습니다.",
            )
        return server
    if not (server.is_public or server.owner_id == user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="접근 권한이 없습니다.",
        )
    return server
