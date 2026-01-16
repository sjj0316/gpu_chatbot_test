from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.dependencies import get_db, get_current_user
from app.routers import conversations as router_module


class FakeUser:
    def __init__(self, user_id: int) -> None:
        self.id = user_id


class _Tx:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


class FakeSession:
    async def commit(self) -> None:
        return None

    def begin(self) -> _Tx:
        return _Tx()

    async def close(self) -> None:
        return None


@pytest.fixture(autouse=True)
def _override_deps() -> None:
    session = FakeSession()

    async def override_db():
        yield session

    def override_user():
        return FakeUser(1)

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_user] = override_user
    yield
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_conversation(monkeypatch: pytest.MonkeyPatch):
    class FakeService:
        def __init__(self, session):
            self.session = session

        async def create_conversation(self, **kwargs):
            return SimpleNamespace(id=1, title=kwargs.get("title"))

    monkeypatch.setattr(router_module, "ChatService", FakeService)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.post(
            "/api/v1/conversations",
            json={"title": "hello", "default_model_key_id": None, "default_params": None},
        )

    assert resp.status_code == 200
    assert resp.json() == {"id": 1, "title": "hello"}


@pytest.mark.asyncio
async def test_list_conversations(monkeypatch: pytest.MonkeyPatch):
    class FakeService:
        def __init__(self, session):
            self.session = session

        async def list_conversations(self, **kwargs):
            return [SimpleNamespace(id=1, title="t1"), SimpleNamespace(id=2, title=None)]

    monkeypatch.setattr(router_module, "ChatService", FakeService)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.get("/api/v1/conversations")

    assert resp.status_code == 200
    assert resp.json() == [{"id": 1, "title": "t1"}, {"id": 2, "title": None}]


@pytest.mark.asyncio
async def test_get_histories_merges_tool_calls(monkeypatch: pytest.MonkeyPatch):
    ts = datetime(2025, 1, 1, tzinfo=timezone.utc)

    rows = [
        SimpleNamespace(
            id=1,
            role=SimpleNamespace(code="user"),
            content="hello",
            timestamp=ts,
            input_tokens=None,
            output_tokens=None,
            cost=None,
            latency_ms=None,
            tool_name=None,
            tool_call_id=None,
            tool_input=None,
            tool_output=None,
            error=None,
        ),
        SimpleNamespace(
            id=2,
            role=SimpleNamespace(code="tool"),
            content=None,
            timestamp=ts,
            input_tokens=None,
            output_tokens=None,
            cost=None,
            latency_ms=10,
            tool_name="search",
            tool_call_id="call-1",
            tool_input='{"q":"x"}',
            tool_output=None,
            error=None,
        ),
        SimpleNamespace(
            id=3,
            role=SimpleNamespace(code="tool"),
            content=None,
            timestamp=ts,
            input_tokens=None,
            output_tokens=None,
            cost=None,
            latency_ms=12,
            tool_name="search",
            tool_call_id="call-1",
            tool_input=None,
            tool_output='{"ok":true}',
            error=None,
        ),
    ]

    class FakeService:
        def __init__(self, session):
            self.session = session

        async def get_histories(self, **kwargs):
            return rows

    monkeypatch.setattr(router_module, "ChatService", FakeService)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.get("/api/v1/conversations/1/histories")

    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert data[0]["role"] == "user"
    assert data[0]["content"] == "hello"
    assert data[1]["role"] == "tool"
    assert data[1]["tool_call_id"] == "call-1"
    assert data[1]["tool_input"] == {"q": "x"}
    assert data[1]["tool_output"] == {"ok": True}


@pytest.mark.asyncio
async def test_delete_conversation(monkeypatch: pytest.MonkeyPatch):
    called: dict[str, int] = {}

    class FakeService:
        def __init__(self, session):
            self.session = session

        async def delete_conversation(self, *, conversation_id: int, user_id: int):
            called["conversation_id"] = conversation_id
            called["user_id"] = user_id

    monkeypatch.setattr(router_module, "ChatService", FakeService)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.delete("/api/v1/conversations/10")

    assert resp.status_code == 200
    assert resp.json() == {"ok": True}
    assert called == {"conversation_id": 10, "user_id": 1}


@pytest.mark.asyncio
async def test_invoke_conversation(monkeypatch: pytest.MonkeyPatch):
    class FakeService:
        def __init__(self, session):
            self.session = session

        async def chat_invoke(self, **kwargs):
            return 1, 2, "ok"

    monkeypatch.setattr(router_module, "ChatService", FakeService)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.post(
            "/api/v1/conversations/1/invoke",
            json={"message": "hi"},
        )

    assert resp.status_code == 200
    assert resp.json() == {"conversation_id": 1, "message_id": 2, "content": "ok"}


@pytest.mark.asyncio
async def test_stream_conversation(monkeypatch: pytest.MonkeyPatch):
    async def fake_stream(**kwargs):
        yield "chunk", {"delta": "hi"}
        yield "done", {"finish": True}

    class FakeService:
        def __init__(self, session):
            self.session = session

        async def chat_stream(self, **kwargs):
            async for item in fake_stream(**kwargs):
                yield item

    monkeypatch.setattr(router_module, "ChatService", FakeService)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        async with ac.stream(
            "POST",
            "/api/v1/conversations/1/stream",
            json={"message": "hi"},
        ) as resp:
            body = await resp.aread()

    assert resp.status_code == 200
    assert b"event: chunk" in body
    assert b"event: done" in body
