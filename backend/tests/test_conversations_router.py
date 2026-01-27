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
        # 인증 의존성을 위한 id만 가진 간단한 User 객체.
        self.id = user_id


class _Tx:
    # 가짜 세션에서 쓰는 비동기 트랜잭션 컨텍스트 매니저.
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


class FakeSession:
    # 라우터/서비스에 필요한 최소 비동기 세션 인터페이스.
    async def commit(self) -> None:
        return None

    def begin(self) -> _Tx:
        return _Tx()

    async def close(self) -> None:
        return None


@pytest.fixture(autouse=True)
def _override_deps() -> None:
    # 이 모듈의 모든 테스트에서 DB와 현재 사용자 의존성 오버라이드.
    session = FakeSession()

    async def override_db():
        yield session

    def override_user():
        return FakeUser(1)

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_user] = override_user
    yield
    # 각 테스트 후 의존성 오버라이드 정리.
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_conversation(monkeypatch: pytest.MonkeyPatch):
    # 준비: 제공된 제목을 가진 대화를 반환하는 가짜 서비스.
    class FakeService:
        def __init__(self, session):
            self.session = session

        async def create_conversation(self, **kwargs):
            return SimpleNamespace(id=1, title=kwargs.get("title"))

    monkeypatch.setattr(router_module, "ChatService", FakeService)

    # 실행: 대화 생성 엔드포인트 호출.
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.post(
            "/api/v1/conversations",
            json={"title": "hello", "default_model_key_id": None, "default_params": None},
        )

    # 검증: API가 기대 대화 페이로드 반환.
    assert resp.status_code == 200
    assert resp.json() == {"id": 1, "title": "hello"}


@pytest.mark.asyncio
async def test_list_conversations(monkeypatch: pytest.MonkeyPatch):
    # 준비: 대화 목록을 반환하는 가짜 서비스.
    class FakeService:
        def __init__(self, session):
            self.session = session

        async def list_conversations(self, **kwargs):
            return [SimpleNamespace(id=1, title="t1"), SimpleNamespace(id=2, title=None)]

    monkeypatch.setattr(router_module, "ChatService", FakeService)

    # 실행: 현재 사용자 대화 목록 조회.
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.get("/api/v1/conversations")

    # 검증: 응답이 가짜 서비스 출력과 일치.
    assert resp.status_code == 200
    assert resp.json() == [{"id": 1, "title": "t1"}, {"id": 2, "title": None}]


@pytest.mark.asyncio
async def test_get_histories_merges_tool_calls(monkeypatch: pytest.MonkeyPatch):
    # 준비: 동일 tool_call_id를 공유하는 user/tool 행 구성.
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

    # 준비: 가짜 서비스가 raw 행을 라우터에 반환.
    class FakeService:
        def __init__(self, session):
            self.session = session

        async def get_histories(self, **kwargs):
            return rows

    monkeypatch.setattr(router_module, "ChatService", FakeService)

    # 실행: 히스토리 요청 후 라우터가 tool-call 쌍 병합.
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.get("/api/v1/conversations/1/histories")

    # 검증: tool 호출이 JSON 파싱되어 단일 항목으로 병합.
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
    # 준비: delete_conversation에 전달된 인자 캡처.
    called: dict[str, int] = {}

    class FakeService:
        def __init__(self, session):
            self.session = session

        async def delete_conversation(self, *, conversation_id: int, user_id: int):
            called["conversation_id"] = conversation_id
            called["user_id"] = user_id

    monkeypatch.setattr(router_module, "ChatService", FakeService)

    # 실행: 현재 사용자의 대화 삭제.
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.delete("/api/v1/conversations/10")

    # 검증: 서비스 인자 확인 및 API ok 반환.
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}
    assert called == {"conversation_id": 10, "user_id": 1}


@pytest.mark.asyncio
async def test_invoke_conversation(monkeypatch: pytest.MonkeyPatch):
    # 준비: 가짜 서비스가 conversation_id/message_id/content 반환.
    class FakeService:
        def __init__(self, session):
            self.session = session

        async def chat_invoke(self, **kwargs):
            return 1, 2, "ok"

    monkeypatch.setattr(router_module, "ChatService", FakeService)

    # 실행: 메시지로 대화 invoke 호출.
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.post(
            "/api/v1/conversations/1/invoke",
            json={"message": "hi"},
        )

    # 검증: 응답 페이로드가 가짜 서비스 출력과 일치.
    assert resp.status_code == 200
    assert resp.json() == {"conversation_id": 1, "message_id": 2, "content": "ok"}


@pytest.mark.asyncio
async def test_invoke_conversation_with_rag(monkeypatch: pytest.MonkeyPatch):
    captured: dict[str, object] = {}

    class FakeService:
        def __init__(self, session):
            self.session = session

        async def chat_invoke(self, **kwargs):
            captured["rag"] = kwargs.get("rag")
            return 1, 2, "ok"

    monkeypatch.setattr(router_module, "ChatService", FakeService)

    collection_id = "11111111-1111-1111-1111-111111111111"
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.post(
            "/api/v1/conversations/1/invoke",
            json={
                "message": "hi",
                "rag": {
                    "collection_id": collection_id,
                    "query": "q",
                    "limit": 3,
                    "search_type": "keyword",
                },
            },
        )

    assert resp.status_code == 200
    rag = captured["rag"]
    assert rag is not None
    assert str(rag.collection_id) == collection_id
    assert rag.query == "q"
    assert rag.limit == 3
    assert rag.search_type == "keyword"


@pytest.mark.asyncio
async def test_stream_conversation(monkeypatch: pytest.MonkeyPatch):
    # 준비: 두 개 SSE 이벤트를 내보내는 가짜 스트림 생성기.
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

    # 실행: 스트리밍 요청 후 raw 응답 바디 읽기.
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        async with ac.stream(
            "POST",
            "/api/v1/conversations/1/stream",
            json={"message": "hi"},
        ) as resp:
            body = await resp.aread()

    # 검증: SSE 응답에 두 이벤트 타입 포함.
    assert resp.status_code == 200
    assert b"event: chunk" in body
    assert b"event: done" in body
