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
    description="사용자 소유 MCP 서버 연결 정보를 등록합니다.",
    responses={
        400: {"description": "요청 값 오류"},
        401: {"description": "인증 실패"},
        409: {"description": "중복/제약 조건 충돌"},
        422: {"description": "요청 본문 검증 실패"},
        500: {"description": "서버 오류"},
    },
)
async def create_mcp_server(
    body: MCPServerCreate,
    session: SessionDep,
    user: CurrentUser,
):
    """
    Why: 외부 MCP 서버에 대한 연결 정보를 보관해 재사용합니다.

    Auth:
        - 필요: Bearer 토큰

    Request/Response:
        - 요청: 이름/엔드포인트/메타데이터 등
        - 응답: 생성된 MCP 서버 정보

    Errors:
        - 400: 유효하지 않은 입력 값
        - 401/422: 인증 실패 또는 요청 형식 오류

    Side Effects:
        - DB에 MCP 서버 레코드 생성
    """
    _ = user
    service = MCPServerService(session)
    try:
        return await service.create(body, user=user)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e


@router.get(
    "",
    response_model=list[MCPServerRead],
    summary="MCP 서버 목록 조회",
    description="등록된 MCP 서버 목록을 필터/페이지네이션으로 조회합니다.",
    responses={
        401: {"description": "인증 실패"},
        422: {"description": "쿼리 파라미터 검증 실패"},
        500: {"description": "서버 오류"},
    },
)
async def list_mcp_servers(
    session: SessionDep,
    user: CurrentUser,
    q: str | None = Query(None, description="이름/설명 부분 검색"),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    """
    Why: 사용자에게 연결 가능한 MCP 서버 목록을 제공합니다.

    Auth:
        - 필요: Bearer 토큰

    Request/Response:
        - 요청: q/offset/limit
        - 응답: MCP 서버 목록

    Errors:
        - 401/422: 인증 실패 또는 쿼리 형식 오류

    Side Effects:
        - 없음(조회 전용)
    """
    _ = user
    service = MCPServerService(session)
    return await service.get_list(user=user, q=q, offset=offset, limit=limit)


@router.get(
    "/{server_id}",
    response_model=MCPServerRead,
    summary="MCP 서버 단건 조회",
    description="특정 MCP 서버 상세 정보를 조회합니다.",
    responses={
        401: {"description": "인증 실패"},
        403: {"description": "접근 권한 없음"},
        404: {"description": "서버가 존재하지 않음"},
        422: {"description": "경로 파라미터 검증 실패"},
        500: {"description": "서버 오류"},
    },
)
async def get_mcp_server(
    server_id: int,
    session: SessionDep,
    user: CurrentUser,
):
    """
    Why: 특정 MCP 서버의 연결 정보를 확인합니다.

    Auth:
        - 필요: Bearer 토큰(소유자)

    Request/Response:
        - 요청: server_id
        - 응답: MCP 서버 상세

    Errors:
        - 404: 서버가 존재하지 않거나 접근 불가한 경우
        - 401/422: 인증 실패 또는 경로 파라미터 오류

    Side Effects:
        - 없음(조회 전용)
    """
    _ = user
    service = MCPServerService(session)
    try:
        return await service.get(server_id, user=user)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.patch(
    "/{server_id}",
    response_model=MCPServerRead,
    summary="MCP 서버 수정(부분)",
    description="MCP 서버 정보를 부분적으로 수정합니다.",
    responses={
        400: {"description": "요청 값 오류"},
        401: {"description": "인증 실패"},
        403: {"description": "수정 권한 없음"},
        404: {"description": "서버가 존재하지 않음"},
        422: {"description": "요청 본문/경로 검증 실패"},
        500: {"description": "서버 오류"},
    },
)
async def update_mcp_server(
    server_id: int,
    body: MCPServerUpdate,
    session: SessionDep,
    user: CurrentUser,
):
    """
    Why: MCP 서버의 연결 정보 변경을 반영합니다.

    Auth:
        - 필요: Bearer 토큰(소유자)

    Request/Response:
        - 요청: 수정 가능한 필드
        - 응답: 수정된 MCP 서버 정보

    Errors:
        - 400: 입력 값이 유효하지 않은 경우
        - 404: 서버가 존재하지 않거나 접근 불가한 경우
        - 401/422: 인증 실패 또는 요청 형식 오류

    Side Effects:
        - DB MCP 서버 레코드 업데이트
    """
    _ = user
    service = MCPServerService(session)
    try:
        return await service.update(server_id, body, user=user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.delete(
    "/{server_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="MCP 서버 삭제",
    description="등록된 MCP 서버를 삭제합니다.",
    responses={
        401: {"description": "인증 실패"},
        403: {"description": "삭제 권한 없음"},
        404: {"description": "서버가 존재하지 않음"},
        409: {"description": "삭제 불가(참조 중)"},
        422: {"description": "경로 파라미터 검증 실패"},
        500: {"description": "서버 오류"},
    },
)
async def delete_mcp_server(
    server_id: int,
    session: SessionDep,
    user: CurrentUser,
):
    """
    Why: 더 이상 사용하지 않는 MCP 서버 연결을 제거합니다.

    Auth:
        - 필요: Bearer 토큰(소유자)

    Request/Response:
        - 요청: server_id
        - 응답: 없음(204)

    Errors:
        - 409: 다른 리소스가 참조 중인 경우
        - 404: 서버가 존재하지 않거나 접근 불가한 경우
        - 401/422: 인증 실패 또는 경로 파라미터 오류

    Side Effects:
        - DB MCP 서버 레코드 삭제
    """
    _ = user
    service = MCPServerService(session)
    try:
        await service.delete(server_id, user=user)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
    return None
