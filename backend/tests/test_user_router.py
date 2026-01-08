from __future__ import annotations

from types import SimpleNamespace

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.dependencies import get_db, get_current_user
from app.schemas import UserRead
from app.routers import user as router_module


@pytest.fixture(autouse=True)
def _override_db() -> None:
    async def override_db():
        yield None

    app.dependency_overrides[get_db] = override_db
    yield
    app.dependency_overrides.clear()


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


@pytest.mark.asyncio
async def test_register_user_success(monkeypatch: pytest.MonkeyPatch):
    created = SimpleNamespace(
        id=1, username="tester", nickname="Tester", email="test@example.com"
    )

    class FakeService:
        def __init__(self, db):
            self.db = db

        async def create_user(self, user_data):
            return created

    monkeypatch.setattr(router_module, "UserService", FakeService)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.post(
            "/api/v1/users",
            json={
                "username": "tester",
                "password": "password123",
                "nickname": "Tester",
                "email": "test@example.com",
            },
        )

    assert resp.status_code == 201
    assert UserRead(**resp.json()).username == "tester"


@pytest.mark.asyncio
async def test_register_user_duplicate_username(monkeypatch: pytest.MonkeyPatch):
    class FakeService:
        def __init__(self, db):
            self.db = db

        async def create_user(self, user_data):
            raise ValueError("Username already exists")

    monkeypatch.setattr(router_module, "UserService", FakeService)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.post(
            "/api/v1/users",
            json={
                "username": "tester",
                "password": "password123",
                "nickname": "Tester",
                "email": "test@example.com",
            },
        )

    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_register_user_duplicate_email(monkeypatch: pytest.MonkeyPatch):
    class FakeService:
        def __init__(self, db):
            self.db = db

        async def create_user(self, user_data):
            raise ValueError("Email already exists")

    monkeypatch.setattr(router_module, "UserService", FakeService)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.post(
            "/api/v1/users",
            json={
                "username": "tester",
                "password": "password123",
                "nickname": "Tester",
                "email": "test@example.com",
            },
        )

    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_register_user_missing_default_role(monkeypatch: pytest.MonkeyPatch):
    class FakeService:
        def __init__(self, db):
            self.db = db

        async def create_user(self, user_data):
            raise ValueError("Default user role not found")

    monkeypatch.setattr(router_module, "UserService", FakeService)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.post(
            "/api/v1/users",
            json={
                "username": "tester",
                "password": "password123",
                "nickname": "Tester",
                "email": "test@example.com",
            },
        )

    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_list_users_admin_only(monkeypatch: pytest.MonkeyPatch):
    users = [
        SimpleNamespace(
            id=1, username="admin", nickname="Admin", email="admin@example.com"
        ),
        SimpleNamespace(
            id=2, username="user", nickname="User", email="user@example.com"
        ),
    ]

    class FakeService:
        def __init__(self, db):
            self.db = db

        async def list_users(self, *, limit: int = 50, offset: int = 0):
            return users

    monkeypatch.setattr(router_module, "UserService", FakeService)
    _set_current_user(FakeUser(1, "admin"))

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.get("/api/v1/users")

    assert resp.status_code == 200
    assert [UserRead(**item).username for item in resp.json()] == ["admin", "user"]


@pytest.mark.asyncio
async def test_list_users_forbidden_for_non_admin():
    _set_current_user(FakeUser(1, "user"))

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.get("/api/v1/users")

    assert resp.status_code == 403
