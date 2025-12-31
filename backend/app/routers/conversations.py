from __future__ import annotations
import json

from fastapi import APIRouter
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
    return 1


@router.post("", response_model=ConversationRead)
async def create_conversation(
    payload: ConversationCreate,
    session: SessionDep,
    current_user: CurrentUser,
):
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


@router.get("", response_model=list[ConversationListItem])
async def list_conversations(
    session: SessionDep,
    current_user: CurrentUser,
    limit: int = 20,
    offset: int = 0,
):
    svc = ChatService(session)
    rows = await svc.list_conversations(
        user_id=current_user.id, limit=limit, offset=offset
    )
    return [ConversationListItem(id=r.id, title=r.title) for r in rows]


@router.get("/{conversation_id}/histories", response_model=list[HistoryItem])
async def get_histories(
    conversation_id: int, session: SessionDep, current_user: CurrentUser
):
    svc = ChatService(session)
    rows = await svc.get_histories(
        conversation_id=conversation_id, user_id=current_user.id, limit=1000
    )

    merged_tools: dict[str, dict] = {}
    normals: list[tuple[int, HistoryItem]] = []

    def role_of(r) -> str:
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
                    timestamp=(a["start_ts"] or a["end_ts"] or ""),
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


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    session: SessionDep,
    current_user: CurrentUser,
):
    svc = ChatService(session)
    await svc.delete_conversation(
        conversation_id=conversation_id, user_id=current_user.id
    )
    await session.commit()
    return JSONResponse({"ok": True})


@router.post("/{conversation_id}/invoke", response_model=ChatResponse)
async def invoke(
    conversation_id: int,
    payload: ChatRequest,
    session: SessionDep,
    current_user: CurrentUser,
):
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


@router.post("/{conversation_id}/stream")
async def stream(
    conversation_id: int,
    payload: ChatRequest,
    session: SessionDep,
    current_user: CurrentUser,
):
    svc = ChatService(session)

    async def gen():
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
