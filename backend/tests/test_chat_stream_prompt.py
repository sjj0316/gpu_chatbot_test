from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

import pytest
from langchain_core.messages import AIMessage, SystemMessage

from app.services import chat as chat_module


class _EmptyAsyncGen:
    def __aiter__(self):
        return self

    async def __anext__(self):
        raise StopAsyncIteration


@pytest.mark.asyncio
async def test_chat_stream_uses_system_prompt(monkeypatch: pytest.MonkeyPatch):
    # 준비: 시스템 프롬프트가 모델 입력에 포함되는지 검사.
    captured = {}

    class FakeAgent:
        async def astream(self, inputs, config, stream_mode):
            msgs = inputs.get("messages") or []
            assert isinstance(msgs[0], SystemMessage)
            captured["prompt"] = msgs[0].content
            yield ("messages", (AIMessage(content="ok"), {}))

        def astream_events(self, inputs, config, version="v2"):
            return _EmptyAsyncGen()

    async def fake_get_histories(*args, **kwargs):
        return []

    async def fake_get_conversation(*args, **kwargs):
        return SimpleNamespace(id=1, mcp_servers=[], default_model_key_id=1)

    async def fake_get_model_key(*args, **kwargs):
        return SimpleNamespace(
            id=1,
            provider_id=1,
            provider=SimpleNamespace(code="openai"),
            model="gpt-4o-mini",
        )

    session = MagicMock()
    session.add = MagicMock()
    session.flush = AsyncMock()

    svc = chat_module.ChatService(session)
    monkeypatch.setattr(svc, "get_histories", fake_get_histories)
    monkeypatch.setattr(svc, "_get_conversation", fake_get_conversation)
    monkeypatch.setattr(svc, "_get_model_key", fake_get_model_key)
    monkeypatch.setattr(svc, "_role_id", AsyncMock(side_effect=[1, 2, 3]))
    monkeypatch.setattr(chat_module, "load_mcp_tools_from_servers", AsyncMock(return_value=[]))
    monkeypatch.setattr(chat_module, "get_chat_model", MagicMock())
    monkeypatch.setattr(chat_module, "create_react_agent", lambda *a, **k: FakeAgent())

    system_prompt = "SYSTEM_PROMPT_TEST"
    events = []
    async for ev, data in svc.chat_stream(
        user_id=1,
        user=SimpleNamespace(id=1, role=SimpleNamespace(code="user")),
        conversation_id=1,
        message="hi",
        model_key_id=1,
        params=None,
        system_prompt=system_prompt,
        mcp_server_ids=None,
        rag=None,
    ):
        events.append((ev, data))

    assert captured["prompt"] == system_prompt
    assert any(ev == "token" for ev, _ in events)


@pytest.mark.asyncio
async def test_chat_stream_appends_rag_context(monkeypatch: pytest.MonkeyPatch):
    captured = {}

    class FakeAgent:
        async def astream(self, inputs, config, stream_mode):
            msgs = inputs.get("messages") or []
            assert isinstance(msgs[0], SystemMessage)
            captured["prompt"] = msgs[0].content
            yield ("messages", (AIMessage(content="ok"), {}))

        def astream_events(self, inputs, config, version="v2"):
            return _EmptyAsyncGen()

    class FakeDocumentService:
        def __init__(self, session, collection_id, user):
            captured["collection_id"] = collection_id

        async def search(self, **kwargs):
            captured["rag_query"] = kwargs.get("query")
            return [
                {
                    "page_content": "doc text",
                    "metadata": {"source": "doc-1", "chunk_index": 1},
                    "score": 0.12,
                }
            ]

    async def fake_get_histories(*args, **kwargs):
        return []

    async def fake_get_conversation(*args, **kwargs):
        return SimpleNamespace(id=1, mcp_servers=[], default_model_key_id=1)

    async def fake_get_model_key(*args, **kwargs):
        return SimpleNamespace(
            id=1,
            provider_id=1,
            provider=SimpleNamespace(code="openai"),
            model="gpt-4o-mini",
        )

    session = MagicMock()
    session.add = MagicMock()
    session.flush = AsyncMock()

    svc = chat_module.ChatService(session)
    monkeypatch.setattr(svc, "get_histories", fake_get_histories)
    monkeypatch.setattr(svc, "_get_conversation", fake_get_conversation)
    monkeypatch.setattr(svc, "_get_model_key", fake_get_model_key)
    monkeypatch.setattr(svc, "_role_id", AsyncMock(side_effect=[1, 2, 3]))
    monkeypatch.setattr(chat_module, "DocumentService", FakeDocumentService)
    monkeypatch.setattr(
        chat_module, "load_mcp_tools_from_servers", AsyncMock(return_value=[])
    )
    monkeypatch.setattr(chat_module, "get_chat_model", MagicMock())
    monkeypatch.setattr(chat_module, "create_react_agent", lambda *a, **k: FakeAgent())

    system_prompt = "SYSTEM_PROMPT_TEST"
    rag = SimpleNamespace(
        collection_id=UUID("11111111-1111-1111-1111-111111111111"),
        query=None,
        limit=1,
        model_api_key_id=1,
        filter=None,
        search_type="semantic",
    )
    events = []
    async for ev, data in svc.chat_stream(
        user_id=1,
        user=SimpleNamespace(id=1, role=SimpleNamespace(code="user")),
        conversation_id=1,
        message="hi",
        model_key_id=1,
        params=None,
        system_prompt=system_prompt,
        mcp_server_ids=None,
        rag=rag,
    ):
        events.append((ev, data))

    assert captured["rag_query"] == "hi"
    assert "SYSTEM_PROMPT_TEST" in captured["prompt"]
    assert "Retrieved context" in captured["prompt"]
    assert "doc text" in captured["prompt"]
    assert any(ev == "token" for ev, _ in events)
