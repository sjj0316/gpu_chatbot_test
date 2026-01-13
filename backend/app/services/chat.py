from __future__ import annotations
from typing import Any, AsyncIterator, Sequence
import json
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import undefer, selectinload

from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    AIMessage,
    SystemMessage,
    ToolMessage,
    AIMessageChunk,
)

from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from app.models import (
    Conversation,
    ConversationHistory,
    MCPServer,
    ModelApiKey,
    MessageRoleLkp,
)
from app.utils import get_chat_model, load_mcp_tools_from_servers, to_jsonable

ROLE_CODE_USER = "user"
ROLE_CODE_ASSISTANT = "assistant"
ROLE_CODE_TOOL = "tool"
ROLE_CODE_SYSTEM = "system"
SYSTEM_PROMPT_BASE = """
당신은 지능적인 어시스턴트입니다.
- 사용자의 질문에 명확하고 간결하게 답변하세요.
- 가능한 경우, 관련된 맥락이나 배경 지식을 활용하세요.
- MCP 서버에서 제공하는 도구와 프롬프트가 있다면 이를 참고하여 답변 품질을 높이세요.
- 필요 시 단계별로 논리적으로 사고 과정을 설명해 주세요.
"""


def _is_ai_message(msg) -> bool:
    """
    Why: 메시지가 AI 응답인지 판별해 스트리밍 토큰을 구분합니다.

    Args:
        msg: LangChain 메시지 객체.

    Returns:
        bool: AI/assistant 메시지 여부.
    """
    t = getattr(msg, "type", None)  # 'ai' | 'tool' | 'human' | 'system' ...
    if t in ("ai", "assistant"):
        return True
    # 클래스 기반 보강
    if isinstance(msg, AIMessage):
        return True
    if AIMessageChunk is not None and isinstance(msg, AIMessageChunk):
        return True
    return False


def _json_to_str(x: Any, *, max_len: int = 4000) -> str:
    """
    Why: 툴 출력/입력을 안전하게 문자열로 직렬화합니다.

    Contract:
        - JSON 직렬화 실패 시 str(x)로 폴백합니다.
        - max_len 초과 시 잘라냅니다.

    Args:
        x: 직렬화 대상.
        max_len: 최대 길이.

    Returns:
        str: 문자열 표현.
    """
    if x is None:
        return ""
    if isinstance(x, str):
        s = x
    else:
        try:
            s = json.dumps(x, ensure_ascii=False)
        except Exception:
            s = str(x)
    return s if not max_len or len(s) <= max_len else s[:max_len] + "…"


def _mk_ai_toolcall_msg(name: str, call_id: str, args: Any) -> AIMessage:
    """
    Why: 툴 호출 시작 메시지를 AIMessage 형태로 생성합니다.

    Args:
        name: 툴 이름.
        call_id: 호출 식별자.
        args: 툴 입력 인자.

    Returns:
        AIMessage: 툴 호출 메시지.
    """
    return AIMessage(
        content="",
        tool_calls=[
            {
                "id": call_id,
                "name": name,
                "args": args if isinstance(args, (dict, list)) else {},
            }
        ],
    )


def _build_messages_from_histories(
    items: Sequence[ConversationHistory],
    system_prompt: str | None,
) -> list[BaseMessage]:
    """
    Summary: DB 히스토리를 LangChain 메시지 배열로 변환합니다.

    Contract:
        - role 코드에 따라 Human/AI/Tool/System 메시지를 생성합니다.
        - tool_call_id가 있는 경우 tool start/end 메시지를 구성합니다.

    Args:
        items: 히스토리 엔티티 목록.
        system_prompt: 시스템 프롬프트(옵션).

    Returns:
        list[BaseMessage]: LangChain 메시지 목록.
    """
    msgs: list[BaseMessage] = []
    if system_prompt:
        msgs.append(SystemMessage(content=system_prompt))

    for h in items:
        code = (h.role.code or "").lower()
        if code == "user":
            if h.content:
                msgs.append(HumanMessage(content=h.content))

        elif code == "assistant":
            if h.content:
                msgs.append(AIMessage(content=h.content))

        elif code == "tool":
            name = h.tool_name or "tool"
            call_id = h.tool_call_id or ""
            if call_id and h.tool_input is not None:
                msgs.append(_mk_ai_toolcall_msg(name, call_id, h.tool_input))
            if call_id and (h.tool_output is not None or h.content):
                tool_content = h.tool_output if h.tool_output is not None else h.content
                msgs.append(
                    ToolMessage(
                        tool_call_id=call_id,
                        name=name,
                        content=_json_to_str(tool_content),
                    )
                )
        elif code == "system":
            if h.content:
                msgs.append(SystemMessage(content=h.content))

    return msgs


class ChatService:
    def __init__(self, session: AsyncSession):
        """
        Why: 대화/히스토리 관련 작업에 사용할 DB 세션을 주입합니다.

        Args:
            session: 비동기 SQLAlchemy 세션.
        """
        self.session = session
        self._role_id_cache: dict[str, int] = {}

    async def _role_id(self, code: str) -> int:
        """
        Summary: 역할 코드에 대한 ID를 조회하고 캐시합니다.

        Args:
            code: 역할 코드(user/assistant/tool/system).

        Returns:
            int: 역할 ID.

        Side Effects:
            - DB 조회
            - 캐시 갱신
        """
        if code in self._role_id_cache:
            return self._role_id_cache[code]
        res = await self.session.execute(
            select(MessageRoleLkp).where(MessageRoleLkp.code == code)
        )
        row = res.scalar_one()
        self._role_id_cache[code] = row.id
        return row.id

    async def create_conversation(
        self,
        *,
        user_id: int,
        title: str | None,
        default_model_key_id: int | None,
        default_params: dict | None,
        mcp_server_ids: list[int] | None,
    ) -> Conversation:
        """
        Summary: 새 대화를 생성하고 MCP 서버 연결을 설정합니다.

        Args:
            user_id: 사용자 ID.
            title: 대화 제목.
            default_model_key_id: 기본 모델 키.
            default_params: 기본 파라미터.
            mcp_server_ids: 연결할 MCP 서버 ID 목록.

        Returns:
            Conversation: 생성된 대화 엔티티.

        Side Effects:
            - DB 레코드 생성
            - 대화-서버 연관 설정
        """
        q = Conversation(
            user_id=user_id,
            title=title,
            default_model_key_id=default_model_key_id,
            default_params=default_params,
        )
        self.session.add(q)
        await self.session.flush()
        if mcp_server_ids:
            servers = await self._get_mcp_servers(mcp_server_ids)
            q.mcp_servers.extend(servers)
        await self.session.flush()
        return q

    async def list_conversations(
        self, *, user_id: int, limit: int = 20, offset: int = 0
    ) -> list[Conversation]:
        """
        Summary: 사용자의 대화 목록을 최신순으로 조회합니다.

        Args:
            user_id: 사용자 ID.
            limit: 페이지 크기.
            offset: 페이지 시작 위치.

        Returns:
            list[Conversation]: 대화 목록.

        Side Effects:
            - DB 조회
        """
        res = await self.session.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.id.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(res.scalars())

    async def get_histories(
        self, *, conversation_id: int, user_id: int, limit: int = 200
    ) -> list[ConversationHistory]:
        """
        Summary: 대화 히스토리를 시간순으로 조회합니다.

        Args:
            conversation_id: 대화 ID.
            user_id: 사용자 ID.
            limit: 최대 조회 개수.

        Returns:
            list[ConversationHistory]: 히스토리 목록.

        Side Effects:
            - DB 조회
        """
        res = await self.session.execute(
            select(ConversationHistory)
            .join(Conversation, ConversationHistory.conversation_id == Conversation.id)
            .options(
                selectinload(ConversationHistory.role),
            )
            .where(Conversation.id == conversation_id, Conversation.user_id == user_id)
            .order_by(ConversationHistory.id.asc())
            .limit(limit)
        )
        return list(res.scalars())

    async def delete_conversation(self, *, conversation_id: int, user_id: int) -> None:
        """
        Summary: 대화 엔티티를 삭제합니다.

        Args:
            conversation_id: 대화 ID.
            user_id: 사용자 ID.

        Side Effects:
            - DB 레코드 삭제
        """
        res = await self.session.execute(
            select(Conversation).where(
                Conversation.id == conversation_id, Conversation.user_id == user_id
            )
        )
        conv = res.scalar_one()
        await self.session.delete(conv)
        await self.session.flush()

    async def _get_conversation(
        self, *, conversation_id: int | None, user_id: int
    ) -> Conversation:
        """
        Summary: 대화를 조회하거나 없으면 새로 생성합니다.

        Contract:
            - conversation_id가 없으면 신규 대화를 생성합니다.

        Args:
            conversation_id: 대화 ID(옵션).
            user_id: 사용자 ID.

        Returns:
            Conversation: 대화 엔티티.

        Side Effects:
            - DB 조회/생성
        """
        if conversation_id:
            res = await self.session.execute(
                select(Conversation)
                .options(
                    selectinload(Conversation.mcp_servers),
                    selectinload(Conversation.default_model_key).selectinload(
                        ModelApiKey.provider
                    ),
                    selectinload(Conversation.default_model_key).selectinload(
                        ModelApiKey.purpose
                    ),
                )
                .where(
                    Conversation.id == conversation_id, Conversation.user_id == user_id
                )
            )
            return res.scalar_one()
        q = Conversation(user_id=user_id)
        self.session.add(q)
        await self.session.flush()
        return q

    async def _get_model_key(
        self, *, explicit_model_key_id: int | None, conversation: Conversation
    ) -> ModelApiKey:
        """
        Summary: 명시된 또는 대화 기본 모델 키를 조회합니다.

        Args:
            explicit_model_key_id: 명시적 모델 키 ID.
            conversation: 대화 엔티티.

        Returns:
            ModelApiKey: 모델 키 엔티티(비밀값 포함).

        Raises:
            ValueError: 모델 키가 지정되지 않은 경우.

        Side Effects:
            - DB 조회
        """
        target_id = explicit_model_key_id or conversation.default_model_key_id
        if not target_id:
            raise ValueError("model_key_id가 필요합니다.")

        res = await self.session.execute(
            select(ModelApiKey)
            .options(
                undefer(ModelApiKey.api_key),
                selectinload(ModelApiKey.provider),
                selectinload(ModelApiKey.purpose),
            )
            .where(ModelApiKey.id == target_id)
        )
        return res.scalar_one()

    async def _get_mcp_servers(self, ids: list[int]) -> list[MCPServer]:
        """
        Summary: MCP 서버 ID 목록을 조회합니다.

        Args:
            ids: MCP 서버 ID 목록.

        Returns:
            list[MCPServer]: MCP 서버 엔티티 목록.

        Side Effects:
            - DB 조회
        """
        res = await self.session.execute(select(MCPServer).where(MCPServer.id.in_(ids)))
        return list(res.scalars())

    async def chat_invoke(
        self,
        *,
        user_id: int,
        conversation_id: int | None,
        message: str,
        model_key_id: int | None,
        params: dict | None,
        system_prompt: str | None,
        mcp_server_ids: list[int] | None,
    ) -> tuple[int, int, str]:
        """
        Summary: 단일 요청/응답 방식으로 채팅을 수행합니다.

        Contract:
            - 모델 키가 없으면 ValueError를 발생시킵니다.
            - 히스토리를 읽어 메시지 컨텍스트를 구성합니다.

        Args:
            user_id: 사용자 ID.
            conversation_id: 대화 ID(없으면 생성).
            message: 사용자 입력 메시지.
            model_key_id: 사용할 모델 키 ID(옵션).
            params: 모델 파라미터.
            system_prompt: 시스템 프롬프트(옵션).
            mcp_server_ids: MCP 서버 ID 목록(옵션).

        Returns:
            tuple[int, int, str]: (conversation_id, message_id, content).

        Side Effects:
            - DB 히스토리 저장
            - 외부 LLM 호출
        """
        conv = await self._get_conversation(
            conversation_id=conversation_id, user_id=user_id
        )
        model_key = await self._get_model_key(
            explicit_model_key_id=model_key_id, conversation=conv
        )
        if mcp_server_ids:
            servers = await self._get_mcp_servers(mcp_server_ids)
        else:
            servers = conv.mcp_servers
        tools = await load_mcp_tools_from_servers(servers)
        model = get_chat_model(model_key.model, model_key, **(params or {}))
        memory = MemorySaver()
        agent = create_react_agent(model, tools, checkpointer=memory)
        cfg = {"configurable": {"thread_id": str(conversation_id)}}

        user_role_id = await self._role_id(ROLE_CODE_USER)
        assistant_role_id = await self._role_id(ROLE_CODE_ASSISTANT)
        system_role_id = await self._role_id(ROLE_CODE_SYSTEM)
        tool_role_id = await self._role_id(ROLE_CODE_TOOL)
        histories = await self.get_histories(
            conversation_id=conv.id, user_id=user_id, limit=1000
        )
        _ = system_role_id, tool_role_id
        msgs = self._build_messages_from_histories(histories, system_prompt)
        msgs.append(HumanMessage(content=message))
        self.session.add(
            ConversationHistory(
                conversation_id=conv.id, role_id=user_role_id, content=message
            )
        )
        await self.session.flush()
        result = await agent.ainvoke({"messages": msgs}, config=cfg)
        content = (
            result["messages"][-1].content if isinstance(result, dict) else str(result)
        )
        ai = ConversationHistory(
            conversation_id=conv.id,
            role_id=assistant_role_id,
            content=content,
            model_api_key_id=model_key.id,
            model_provider_id=model_key.provider_id,
            model_provider_code=model_key.provider.code,
            model_model=model_key.model,
            params=params,
        )
        self.session.add(ai)
        await self.session.flush()
        return conv.id, ai.id, content

    async def chat_stream(
        self,
        *,
        user_id: int,
        conversation_id: int | None,
        message: str,
        model_key_id: int | None,
        params: dict | None,
        system_prompt: str | None,
        mcp_server_ids: list[int] | None,
    ) -> AsyncIterator[tuple[str, dict]]:
        """
        Summary: 스트리밍 방식으로 채팅 이벤트를 생성합니다.

        Contract:
            - SSE 이벤트 이름과 payload를 튜플로 yield합니다.
            - tool 이벤트는 별도 히스토리로 저장합니다.

        Args:
            user_id: 사용자 ID.
            conversation_id: 대화 ID(없으면 생성).
            message: 사용자 입력 메시지.
            model_key_id: 사용할 모델 키 ID(옵션).
            params: 모델 파라미터.
            system_prompt: 시스템 프롬프트(옵션).
            mcp_server_ids: MCP 서버 ID 목록(옵션).

        Yields:
            tuple[str, dict]: (event_name, payload).

        Side Effects:
            - DB 히스토리 저장
            - 외부 LLM 호출
        """
        conv = await self._get_conversation(
            conversation_id=conversation_id, user_id=user_id
        )
        conv_id = conv.id
        model_key = await self._get_model_key(
            explicit_model_key_id=model_key_id, conversation=conv
        )
        provider_id = model_key.provider_id
        provider_code = model_key.provider.code
        model_name = model_key.model
        model_key_id_val = model_key.id

        if mcp_server_ids:
            servers = await self._get_mcp_servers(mcp_server_ids)
        else:
            servers = list(conv.mcp_servers)

        user_role_id = await self._role_id(ROLE_CODE_USER)
        assistant_role_id = await self._role_id(ROLE_CODE_ASSISTANT)
        tool_role_id = await self._role_id(ROLE_CODE_TOOL)

        tools = await load_mcp_tools_from_servers(servers)
        histories = await self.get_histories(
            conversation_id=conv_id, user_id=user_id, limit=1000
        )
        msgs = _build_messages_from_histories(histories, SYSTEM_PROMPT_BASE)
        msgs.append(HumanMessage(content=message))

        self.session.add(
            ConversationHistory(
                conversation_id=conv_id, role_id=user_role_id, content=message
            )
        )
        await self.session.flush()

        model = get_chat_model(model_name, model_key, **(params or {}))
        memory = MemorySaver()
        agent = create_react_agent(model, tools, checkpointer=memory)
        cfg = {"configurable": {"thread_id": str(conv_id)}}

        parts: list[str] = []
        q: asyncio.Queue[tuple[str, dict]] = asyncio.Queue()

        async def consume_events():
            """
            Summary: LangGraph 이벤트를 구독해 툴 호출 상태를 큐로 전달합니다.

            Contract:
                - on_tool_start/on_tool_end만 처리합니다.

            Side Effects:
                - DB 히스토리 저장
                - SSE 큐 적재
            """
            try:
                async for ev in agent.astream_events(
                    {"messages": msgs}, config=cfg, version="v2"
                ):
                    kind = ev.get("event")  # 예: "on_tool_start", "on_tool_end"
                    name = ev.get("name")  # 툴 이름
                    run_id = ev.get("run_id") or ev.get("id")  # 호출 식별자
                    data = ev.get("data") or {}

                    if kind == "on_tool_start":
                        # 입력 인자 추출 (스키마에 따라 data에 포함)
                        tool_input = (
                            data.get("input") if isinstance(data, dict) else None
                        )
                        row = ConversationHistory(
                            conversation_id=conv_id,
                            role_id=tool_role_id,
                            content=None,
                            tool_name=name,
                            tool_call_id=str(run_id) if run_id else None,
                            tool_input=to_jsonable(tool_input),
                        )
                        self.session.add(row)
                        await self.session.flush()
                        await q.put(
                            (
                                "tool_start",
                                {
                                    "tool_call_id": row.tool_call_id,
                                    "tool_name": name,
                                    "args": row.tool_input or {},
                                    "message_id": row.id,
                                },
                            )
                        )

                    elif kind == "on_tool_end":
                        # 결과/에러 추출 (LangChain 콜백/이벤트 규격)
                        raw_output = (
                            data.get("output") if isinstance(data, dict) else None
                        )
                        raw_error = (
                            data.get("error") if isinstance(data, dict) else None
                        )
                        safe_output = (
                            to_jsonable(raw_output, max_str_len=3000)
                            if raw_output is not None
                            else None
                        )
                        safe_error = (
                            to_jsonable(raw_error, max_str_len=3000)
                            if raw_error is not None
                            else None
                        )

                        row = ConversationHistory(
                            conversation_id=conv_id,
                            role_id=tool_role_id,
                            content=None,
                            tool_name=name,
                            tool_call_id=str(run_id) if run_id else None,
                            tool_output=safe_output,
                            error=(str(safe_error) if safe_error else None),
                        )
                        self.session.add(row)
                        await self.session.flush()
                        await q.put(
                            (
                                "tool_end",
                                {
                                    "tool_call_id": row.tool_call_id,
                                    "tool_name": name,
                                    "ok": raw_error is None,
                                    "output": (
                                        row.tool_output if raw_error is None else None
                                    ),
                                    "error": row.error,
                                    "message_id": row.id,
                                },
                            )
                        )

                    # 필요시 다른 이벤트도 필터링 가능:
                    # - "on_chat_model_stream", "on_chain_start/end" 등
            except Exception as e:
                import traceback

                tb = "".join(traceback.format_exception(type(e), e, e.__traceback__))[
                    :8000
                ]
                await q.put(("error", {"message": str(e), "traceback": tb}))

        ev_task = asyncio.create_task(consume_events())
        try:
            async for mode, payload in agent.astream(
                {"messages": msgs}, config=cfg, stream_mode=["messages", "updates"]
            ):
                # 이벤트 큐 비우기 → SSE로 전달
                while not q.empty():
                    k, p = await q.get()
                    yield (k, p)

                if mode == "messages":
                    msg, meta = payload
                    text = getattr(msg, "content", None)
                    s = str(text) if text is not None else str(msg)
                    if s and _is_ai_message(msg):
                        parts.append(s)
                        yield ("token", {"text": s})

                elif mode == "updates":
                    yield ("update", {"note": str(payload)})
        finally:
            # 남은 이벤트 배출 후 태스크 종료 대기
            await asyncio.sleep(0)
            while not q.empty():
                k, p = await q.get()
                yield (k, p)
            try:
                await asyncio.wait_for(ev_task, timeout=0.1)
            except Exception:
                pass

        # 최종 답변 저장 (툴 결과는 포함 안 함)
        final_text = "".join(parts)
        ai = ConversationHistory(
            conversation_id=conv_id,
            role_id=assistant_role_id,
            content=final_text,
            model_api_key_id=model_key_id_val,
            model_provider_id=provider_id,
            model_provider_code=provider_code,
            model_model=model_name,
            params=params,
        )
        self.session.add(ai)
        await self.session.flush()

        yield (
            "done",
            {"conversation_id": conv_id, "message_id": ai.id, "content": final_text},
        )
