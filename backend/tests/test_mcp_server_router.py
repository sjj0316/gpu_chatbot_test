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
        self.code = code


class FakeUser:
    def __init__(self, user_id: int, role_code: str = "user") -> None:
        self.id = user_id
        self.role = FakeRole(role_code)


def _set_current_user(user: FakeUser) -> None:
    def override_user():
        return user

    app.dependency_overrides[get_current_user] = override_user


@pytest.fixture(autouse=True)
def _override_db() -> None:
    async def override_db():
        yield None

    app.dependency_overrides[get_db] = override_db
    yield
    app.dependency_overrides.clear()


def _make_server(server_id: int = 1) -> SimpleNamespace:
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

    assert resp.status_code == 201
    assert received["user_id"] == 1
    assert MCPServerRead(**resp.json()).name == "Demo MCP"


@pytest.mark.asyncio
async def test_list_mcp_servers_uses_current_user(monkeypatch: pytest.MonkeyPatch):
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

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.get("/api/v1/mcp-servers")

    assert resp.status_code == 200
    assert received["user_id"] == 2


@pytest.mark.asyncio
async def test_update_mcp_server_forbidden_from_service(monkeypatch: pytest.MonkeyPatch):
    class FakeService:
        def __init__(self, session):
            self.session = session

        async def update(self, server_id, body, *, user):
            from fastapi import HTTPException

            raise HTTPException(status_code=403, detail="forbidden")

    monkeypatch.setattr(router_module, "MCPServerService", FakeService)
    _set_current_user(FakeUser(1, "user"))

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.patch(
            "/api/v1/mcp-servers/1",
            json={"name": "Updated", "config": {"transport": "http", "url": "http://x"}},
        )

    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_update_mcp_server_success(monkeypatch: pytest.MonkeyPatch):
    updated = _make_server()

    class FakeService:
        def __init__(self, session):
            self.session = session

        async def update(self, server_id, body, *, user):
            return updated

    monkeypatch.setattr(router_module, "MCPServerService", FakeService)
    _set_current_user(FakeUser(1, "user"))

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.patch(
            "/api/v1/mcp-servers/1",
            json={"name": "Updated", "config": {"transport": "http", "url": "http://x"}},
        )

    assert resp.status_code == 200
    assert MCPServerRead(**resp.json()).name == "Demo MCP"


@pytest.mark.asyncio
async def test_delete_mcp_server_forbidden_from_service(monkeypatch: pytest.MonkeyPatch):
    class FakeService:
        def __init__(self, session):
            self.session = session

        async def delete(self, server_id, *, user):
            from fastapi import HTTPException

            raise HTTPException(status_code=403, detail="forbidden")

    monkeypatch.setattr(router_module, "MCPServerService", FakeService)
    _set_current_user(FakeUser(1, "user"))

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.delete("/api/v1/mcp-servers/1")

    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_delete_mcp_server_success(monkeypatch: pytest.MonkeyPatch):
    called = {"delete": False}

    class FakeService:
        def __init__(self, session):
            self.session = session

        async def delete(self, server_id, *, user):
            called["delete"] = True

    monkeypatch.setattr(router_module, "MCPServerService", FakeService)
    _set_current_user(FakeUser(1, "user"))

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.delete("/api/v1/mcp-servers/1")

    assert resp.status_code == 204
    assert called["delete"] is True
