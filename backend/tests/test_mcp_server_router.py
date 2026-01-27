from __future__ import annotations

from types import SimpleNamespace

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.dependencies import get_db, get_current_user
from app.schemas import MCPServerRead
from app.routers import mcp_server as router_module


class FakeRole:
    def __init__(self, code: str) -> None:
        # 접근 규칙 제어용 최소 Role 객체.
        self.code = code


class FakeUser:
    def __init__(self, user_id: int, role_code: str = "user") -> None:
        # get_current_user가 반환하는 최소 User 객체.
        self.id = user_id
        self.role = FakeRole(role_code)


def _set_current_user(user: FakeUser) -> None:
    # 테스트에서 다른 역할을 시뮬레이션하도록 인증 의존성 오버라이드.
    def override_user():
        return user

    app.dependency_overrides[get_current_user] = override_user


@pytest.fixture(autouse=True)
def _override_db() -> None:
    # DB 의존성 오버라이드로 실 DB 접근 회피.
    async def override_db():
        yield None

    app.dependency_overrides[get_db] = override_db
    yield
    # 각 테스트 후 오버라이드 초기화.
    app.dependency_overrides.clear()


def _make_server(server_id: int = 1) -> SimpleNamespace:
    # 라우터 응답용 일관된 가짜 MCP 서버 모델 생성.
    return SimpleNamespace(
        id=server_id,
        name="Demo MCP",
        description="test",
        config={"transport": "http", "url": "http://localhost:9000"},
        is_public=False,
        owner_id=1,
        runtime=None,
    )


@pytest.mark.asyncio
async def test_create_mcp_server_allows_user(monkeypatch: pytest.MonkeyPatch):
    # 준비: 가짜 서비스가 생성된 서버 반환 및 사용자 정보 캡처.
    created = _make_server()
    received: dict[str, int] = {}

    class FakeService:
        def __init__(self, session):
            self.session = session

        async def create(self, body, *, user):
            received["user_id"] = user.id
            return created

    monkeypatch.setattr(router_module, "MCPServerService", FakeService)
    _set_current_user(FakeUser(1, "user"))

    # 실행: 일반 사용자로 MCP 서버 생성.
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.post(
            "/api/v1/mcp-servers",
            json={
                "name": "Demo MCP",
                "description": "test",
                "config": {"transport": "http", "url": "http://localhost:9000"},
            },
        )

    # 검증: 생성 성공 및 서비스가 현재 사용자 수신.
    assert resp.status_code == 201
    assert received["user_id"] == 1
    assert MCPServerRead(**resp.json()).name == "Demo MCP"


@pytest.mark.asyncio
async def test_create_mcp_server_conflict(monkeypatch: pytest.MonkeyPatch):
    # 준비: 서비스가 중복 에러를 ValueError로 반환.
    class FakeService:
        def __init__(self, session):
            self.session = session

        async def create(self, body, *, user):
            raise ValueError("duplicate")

    monkeypatch.setattr(router_module, "MCPServerService", FakeService)
    _set_current_user(FakeUser(1, "user"))

    # 실행: 중복 서버 생성 시도.
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.post(
            "/api/v1/mcp-servers",
            json={
                "name": "Demo MCP",
                "description": "test",
                "config": {"transport": "http", "url": "http://localhost:9000"},
            },
        )

    # 검증: 409 응답.
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_list_mcp_servers_uses_current_user(monkeypatch: pytest.MonkeyPatch):
    # 준비: 가짜 서비스가 목록 반환 및 user id 캡처.
    received: dict[str, int] = {}
    created = _make_server()

    class FakeService:
        def __init__(self, session):
            self.session = session

        async def get_list(self, *, user, **kwargs):
            received["user_id"] = user.id
            return [created]

    monkeypatch.setattr(router_module, "MCPServerService", FakeService)
    _set_current_user(FakeUser(2, "user"))

    # 실행: 현재 사용자로 MCP 서버 목록 조회.
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.get("/api/v1/mcp-servers")

    # 검증: 서비스가 올바른 user id 수신.
    assert resp.status_code == 200
    assert received["user_id"] == 2


@pytest.mark.asyncio
async def test_update_mcp_server_forbidden_from_service(monkeypatch: pytest.MonkeyPatch):
    # 준비: 가짜 서비스가 403 HTTPException 발생.
    class FakeService:
        def __init__(self, session):
            self.session = session

        async def update(self, server_id, body, *, user):
            from fastapi import HTTPException

            raise HTTPException(status_code=403, detail="forbidden")

    monkeypatch.setattr(router_module, "MCPServerService", FakeService)
    _set_current_user(FakeUser(1, "user"))

    # 실행: 서버 업데이트 시도.
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.patch(
            "/api/v1/mcp-servers/1",
            json={"name": "Updated", "config": {"transport": "http", "url": "http://x"}},
        )

    # 검증: 403 응답.
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_update_mcp_server_success(monkeypatch: pytest.MonkeyPatch):
    # 준비: 가짜 서비스가 업데이트된 서버 반환.
    updated = _make_server()

    class FakeService:
        def __init__(self, session):
            self.session = session

        async def update(self, server_id, body, *, user):
            return updated

    monkeypatch.setattr(router_module, "MCPServerService", FakeService)
    _set_current_user(FakeUser(1, "user"))

    # 실행: 소유자로 서버 업데이트.
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.patch(
            "/api/v1/mcp-servers/1",
            json={"name": "Updated", "config": {"transport": "http", "url": "http://x"}},
        )

    # 검증: API가 업데이트된 서버 페이로드 반환.
    assert resp.status_code == 200
    assert MCPServerRead(**resp.json()).name == "Demo MCP"


@pytest.mark.asyncio
async def test_delete_mcp_server_forbidden_from_service(monkeypatch: pytest.MonkeyPatch):
    # 준비: 삭제 시 403 HTTPException 발생.
    class FakeService:
        def __init__(self, session):
            self.session = session

        async def delete(self, server_id, *, user):
            from fastapi import HTTPException

            raise HTTPException(status_code=403, detail="forbidden")

    monkeypatch.setattr(router_module, "MCPServerService", FakeService)
    _set_current_user(FakeUser(1, "user"))

    # 실행: 서버 삭제 시도.
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.delete("/api/v1/mcp-servers/1")

    # 검증: 403 응답.
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_delete_mcp_server_success(monkeypatch: pytest.MonkeyPatch):
    # 준비: delete 호출 시 플래그를 토글하는 가짜 서비스.
    called = {"delete": False}

    class FakeService:
        def __init__(self, session):
            self.session = session

        async def delete(self, server_id, *, user):
            called["delete"] = True

    monkeypatch.setattr(router_module, "MCPServerService", FakeService)
    _set_current_user(FakeUser(1, "user"))

    # 실행: 소유자로 서버 삭제.
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.delete("/api/v1/mcp-servers/1")

    # 검증: 삭제 성공 및 서비스 메서드 호출.
    assert resp.status_code == 204
    assert called["delete"] is True
