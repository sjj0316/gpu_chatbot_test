from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, status

from app.dependencies import SessionDep, CurrentUser
from app.schemas import (
    MCPServerCreate,
    MCPServerRead,
    MCPServerUpdate,
)
from app.services import MCPServerService

router = APIRouter(prefix="/mcp-servers", tags=["MCP Servers"])


@router.post(
    "",
    response_model=MCPServerRead,
    status_code=status.HTTP_201_CREATED,
    summary="MCP 서버 생성",
)
async def create_mcp_server(
    body: MCPServerCreate,
    session: SessionDep,
    user: CurrentUser,
):
    _ = user
    service = MCPServerService(session)
    try:
        return await service.create(body, user=user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "",
    response_model=list[MCPServerRead],
    summary="MCP 서버 목록 조회",
)
async def list_mcp_servers(
    session: SessionDep,
    user: CurrentUser,
    q: str | None = Query(None, description="이름/설명 부분 검색"),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    _ = user
    service = MCPServerService(session)
    return await service.get_list(user=user, q=q, offset=offset, limit=limit)


@router.get(
    "/{server_id}",
    response_model=MCPServerRead,
    summary="MCP 서버 단건 조회",
)
async def get_mcp_server(
    server_id: int,
    session: SessionDep,
    user: CurrentUser,
):
    _ = user
    service = MCPServerService(session)
    try:
        return await service.get(server_id, user=user)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch(
    "/{server_id}",
    response_model=MCPServerRead,
    summary="MCP 서버 수정(부분)",
)
async def update_mcp_server(
    server_id: int,
    body: MCPServerUpdate,
    session: SessionDep,
    user: CurrentUser,
):
    _ = user
    service = MCPServerService(session)
    try:
        return await service.update(server_id, body, user=user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/{server_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="MCP 서버 삭제",
)
async def delete_mcp_server(
    server_id: int,
    session: SessionDep,
    user: CurrentUser,
):
    _ = user
    service = MCPServerService(session)
    try:
        await service.delete(server_id, user=user)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return None
