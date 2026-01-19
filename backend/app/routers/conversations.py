from __future__ import annotations
from datetime import datetime, timezone
import json

from fastapi import APIRouter, Query
from starlette.responses import StreamingResponse, JSONResponse

from app.schemas import (
    ConversationCreate,
    ConversationRead,
    ConversationListItem,
    HistoryItem,
    ChatRequest,
    ChatResponse,
    ChatChunk,
)
from app.services import ChatService
from app.dependencies import SessionDep, CurrentUser
from app.utils import parse_jsonish


router = APIRouter(prefix="/conversations", tags=["Conversation"])


async def get_user_id() -> int:
    """
    Why: 테스트/데모용 사용자 식별자를 반환하는 임시 헬퍼입니다.

    Returns:
        int: 고정 사용자 ID.

    Side Effects:
        없음.
    """
    return 1


@router.post(
    "",
    response_model=ConversationRead,
    summary="대화 생성",
    description="새 대화를 생성하고 기본 모델 설정을 저장합니다.",
    responses={
        401: {"description": "인증 실패"},
        422: {"description": "요청 본문 검증 실패"},
        500: {"description": "서버 오류"},
    },
)
async def create_conversation(
    payload: ConversationCreate,
    session: SessionDep,
    current_user: CurrentUser,
):
    """
    Why: 사용자의 채팅 컨텍스트를 분리된 대화로 관리합니다.

    Auth:
        - 필요: Bearer 토큰

    Request/Response:
        - 요청: title/default_model_key_id/default_params/mcp_server_ids
        - 응답: 생성된 대화 요약

    Errors:
        - 401/422: 인증 실패 또는 요청 형식 오류

    Side Effects:
        - DB 대화 레코드 생성
    """
    svc = ChatService(session)
    conv = await svc.create_conversation(
        user_id=current_user.id,
        title=payload.title,
        default_model_key_id=payload.default_model_key_id,
        default_params=payload.default_params,
        mcp_server_ids=payload.mcp_server_ids or None,
    )
    await session.commit()
    return ConversationRead(id=conv.id, title=conv.title)


@router.get(
    "",
    response_model=list[ConversationListItem],
    summary="대화 목록 조회",
    description="현재 사용자의 대화 목록을 페이지네이션으로 조회합니다.",
    responses={
        401: {"description": "인증 실패"},
        422: {"description": "쿼리 파라미터 검증 실패"},
        500: {"description": "서버 오류"},
    },
)
async def list_conversations(
    session: SessionDep,
    current_user: CurrentUser,
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """
    Why: 사용자가 기존 대화를 선택/재개할 수 있게 합니다.

    Auth:
        - 필요: Bearer 토큰

    Request/Response:
        - 요청: limit/offset
        - 응답: 대화 목록

    Errors:
        - 401/422: 인증 실패 또는 쿼리 형식 오류

    Side Effects:
        - 없음(조회 전용)
    """
    svc = ChatService(session)
    rows = await svc.list_conversations(
        user_id=current_user.id, limit=limit, offset=offset
    )
    return [ConversationListItem(id=r.id, title=r.title) for r in rows]


@router.get(
    "/{conversation_id}/histories",
    response_model=list[HistoryItem],
    summary="대화 히스토리 조회",
    description="대화의 메시지/툴 호출 히스토리를 시간순으로 조회합니다.",
    responses={
        401: {"description": "인증 실패"},
        403: {"description": "접근 권한 없음"},
        404: {"description": "대화를 찾을 수 없음"},
        422: {"description": "경로 파라미터 검증 실패"},
        500: {"description": "서버 오류"},
    },
)
async def get_histories(
    conversation_id: int, session: SessionDep, current_user: CurrentUser
):
    """
    Why: 대화 기록과 툴 호출 결과를 재구성해 UI에서 일관되게 렌더링합니다.

    Auth:
        - 필요: Bearer 토큰(소유자)

    Request/Response:
        - 요청: conversation_id
        - 응답: 메시지/툴 호출 히스토리 목록

    Errors:
        - 403/404: 권한 없음 또는 대화 미존재
        - 401/422: 인증 실패 또는 경로 파라미터 오류

    Side Effects:
        - 없음(조회 전용)
    """
    svc = ChatService(session)
    rows = await svc.get_histories(
        conversation_id=conversation_id, user_id=current_user.id, limit=1000
    )

    merged_tools: dict[str, dict] = {}
    normals: list[tuple[int, HistoryItem]] = []

    def role_of(r) -> str:
        """
        Why: DB 저장 포맷을 UI 표준 role("user"/"assistant"/"tool"/"system")로 정규화합니다.

        Args:
            r: DB에서 조회된 히스토리 행.

        Returns:
            str: 표준 role 문자열.

        Side Effects:
            없음.
        """
        code = (r.role.code or "").lower()
        return (
            "assistant"
            if code == "assistant"
            else "system" if code == "system" else "tool" if code == "tool" else "user"
        )

    for r in rows:
        role = role_of(r)
        if role != "tool" or not getattr(r, "tool_call_id", None):
            normals.append(
                (
                    r.id,
                    HistoryItem(
                        id=r.id,
                        role=role,
                        content=r.content,
                        timestamp=r.timestamp.isoformat(),
                        input_tokens=r.input_tokens,
                        output_tokens=r.output_tokens,
                        cost=float(r.cost) if r.cost is not None else None,
                        latency_ms=r.latency_ms,
                        tool_name=getattr(r, "tool_name", None),
                        tool_call_id=getattr(r, "tool_call_id", None),
                        tool_input=parse_jsonish(getattr(r, "tool_input", None)),
                        tool_output=parse_jsonish(getattr(r, "tool_output", None)),
                        error=getattr(r, "error", None),
                    ),
                )
            )
            continue

        # tool row: aggregate by tool_call_id
        call_id = r.tool_call_id
        agg = merged_tools.get(call_id)
        if not agg:
            agg = merged_tools[call_id] = {
                "first_id": r.id,
                "tool_name": getattr(r, "tool_name", None),
                "tool_call_id": call_id,
                "input": None,
                "output": None,
                "error": None,
                "start_ts": None,
                "end_ts": None,
                "latency_ms": None,
            }
        agg["first_id"] = min(agg["first_id"], r.id)
        if getattr(r, "tool_input", None) is not None:
            agg["input"] = parse_jsonish(r.tool_input)
            agg["start_ts"] = agg["start_ts"] or r.timestamp.isoformat()
        if getattr(r, "tool_output", None) is not None or r.content:
            agg["output"] = parse_jsonish(getattr(r, "tool_output", None)) or r.content
            agg["end_ts"] = r.timestamp.isoformat()
        if getattr(r, "error", None):
            agg["error"] = str(r.error)
        if getattr(r, "latency_ms", None) is not None:
            agg["latency_ms"] = r.latency_ms

    for call_id, a in sorted(merged_tools.items(), key=lambda kv: kv[1]["first_id"]):
        normals.append(
            (
                a["first_id"],
                    HistoryItem(
                        id=a["first_id"],
                        role="tool",
                        content=None,
                        timestamp=(
                            a["start_ts"]
                            or a["end_ts"]
                            or datetime.now(timezone.utc).isoformat()
                        ),
                        input_tokens=None,
                        output_tokens=None,
                        cost=None,
                    latency_ms=a["latency_ms"],
                    tool_name=a["tool_name"],
                    tool_call_id=a["tool_call_id"],
                    tool_input=a["input"],
                    tool_output=a["output"],
                    error=a["error"],
                ),
            )
        )

    normals.sort(key=lambda t: t[0])
    return [it for _, it in normals]


@router.delete(
    "/{conversation_id}",
    summary="대화 삭제",
    description="대화와 관련 히스토리를 삭제합니다.",
    responses={
        401: {"description": "인증 실패"},
        403: {"description": "접근 권한 없음"},
        404: {"description": "대화를 찾을 수 없음"},
        422: {"description": "경로 파라미터 검증 실패"},
        500: {"description": "서버 오류"},
    },
)
async def delete_conversation(
    conversation_id: int,
    session: SessionDep,
    current_user: CurrentUser,
):
    """
    Why: 불필요한 대화를 제거해 사용자 히스토리를 정리합니다.

    Auth:
        - 필요: Bearer 토큰(소유자)

    Request/Response:
        - 요청: conversation_id
        - 응답: {"ok": true}

    Errors:
        - 403/404: 권한 없음 또는 대화 미존재
        - 401/422: 인증 실패 또는 경로 파라미터 오류

    Side Effects:
        - DB 대화 및 히스토리 삭제
    """
    svc = ChatService(session)
    await svc.delete_conversation(
        conversation_id=conversation_id, user_id=current_user.id
    )
    await session.commit()
    return JSONResponse({"ok": True})


@router.post(
    "/{conversation_id}/invoke",
    response_model=ChatResponse,
    summary="대화 요청(동기)",
    description="지정된 대화에 메시지를 보내고 응답을 반환합니다.",
    responses={
        401: {"description": "인증 실패"},
        403: {"description": "접근 권한 없음"},
        404: {"description": "대화를 찾을 수 없음"},
        422: {"description": "요청 본문/경로 검증 실패"},
        500: {"description": "서버 오류"},
    },
)
async def invoke(
    conversation_id: int,
    payload: ChatRequest,
    session: SessionDep,
    current_user: CurrentUser,
):
    """
    Why: UI에서 동기 방식으로 답변을 받을 수 있게 합니다.

    Auth:
        - 필요: Bearer 토큰(소유자)

    Request/Response:
        - 요청: message/model_key_id/params/system_prompt/mcp_server_ids
        - 응답: conversation_id/message_id/content

    Errors:
        - 403/404: 권한 없음 또는 대화 미존재
        - 401/422: 인증 실패 또는 요청 형식 오류

    Side Effects:
        - DB 히스토리 저장
        - 외부 LLM API 호출
    """
    svc = ChatService(session)
    conv_id, msg_id, content = await svc.chat_invoke(
        user_id=current_user.id,
        conversation_id=conversation_id,
        message=payload.message,
        model_key_id=payload.model_key_id,
        params=payload.params,
        system_prompt=payload.system_prompt,
        mcp_server_ids=payload.mcp_server_ids or None,
    )
    await session.commit()
    return ChatResponse(conversation_id=conv_id, message_id=msg_id, content=content)


@router.post(
    "/{conversation_id}/stream",
    summary="대화 요청(스트리밍)",
    description="SSE로 토큰 스트리밍 응답을 전송합니다.",
    responses={
        401: {"description": "인증 실패"},
        403: {"description": "접근 권한 없음"},
        404: {"description": "대화를 찾을 수 없음"},
        422: {"description": "요청 본문/경로 검증 실패"},
        500: {"description": "서버 오류"},
    },
)
async def stream(
    conversation_id: int,
    payload: ChatRequest,
    session: SessionDep,
    current_user: CurrentUser,
):
    """
    Why: 긴 응답을 토큰 단위로 전달해 UI 체감 속도를 높입니다.

    Auth:
        - 필요: Bearer 토큰(소유자)

    Request/Response:
        - 요청: message/model_key_id/params/system_prompt/mcp_server_ids
        - 응답: text/event-stream(SSE)

    Errors:
        - 403/404: 권한 없음 또는 대화 미존재
        - 401/422: 인증 실패 또는 요청 형식 오류

    Side Effects:
        - DB 히스토리 저장
        - 외부 LLM API 호출
    """
    svc = ChatService(session)

    async def gen():
        """
        Why: 스트리밍 이벤트를 생성해 SSE 포맷으로 전달합니다.

        Side Effects:
            - DB 트랜잭션 처리
            - 외부 LLM 호출
        """
        tx = session.begin()
        try:
            async with tx:
                async for ev, data in svc.chat_stream(
                    user_id=current_user.id,
                    conversation_id=conversation_id,
                    message=payload.message,
                    model_key_id=payload.model_key_id,
                    params=payload.params,
                    system_prompt=payload.system_prompt,
                    mcp_server_ids=payload.mcp_server_ids or None,
                ):
                    yield f"event: {ev}\n"
                    yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
        except Exception as e:
            yield "event: error\n"
            yield f"data: {json.dumps({'detail': str(e)}, ensure_ascii=False)}\n\n"
        finally:
            try:
                await session.close()
            except Exception:
                pass

    return StreamingResponse(
        gen(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
