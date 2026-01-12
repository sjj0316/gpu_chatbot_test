from __future__ import annotations

from types import SimpleNamespace

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.dependencies import get_db, get_current_user
from app.routers import auth as router_module


class FakeUser:
    def __init__(self, user_id: int) -> None:
        self.id = user_id


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


@pytest.mark.asyncio
async def test_login_invalid_credentials(monkeypatch: pytest.MonkeyPatch):
    class FakeService:
        def __init__(self, db):
            self.db = db

        async def authenticate_user(self, login_data):
            return None

    monkeypatch.setattr(router_module, "AuthService", FakeService)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.post(
            "/api/v1/auth/login",
            json={"username": "tester", "password": "wrong"},
        )

    assert resp.status_code == 401
    assert resp.json()["detail"] == "아이디 또는 비밀번호가 올바르지 않습니다."


@pytest.mark.asyncio
async def test_change_password_mismatch():
    _set_current_user(FakeUser(1))

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": "old",
                "new_password": "new1",
                "confirm_password": "new2",
            },
        )

    assert resp.status_code == 400
    assert resp.json()["detail"] == "새 비밀번호가 일치하지 않습니다."


@pytest.mark.asyncio
async def test_change_password_same_as_current():
    _set_current_user(FakeUser(1))

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": "same",
                "new_password": "same",
                "confirm_password": "same",
            },
        )

    assert resp.status_code == 400
    assert resp.json()["detail"] == "새 비밀번호는 현재 비밀번호와 달라야 합니다."


@pytest.mark.asyncio
async def test_change_password_invalid_current(monkeypatch: pytest.MonkeyPatch):
    _set_current_user(FakeUser(1))

    class FakeService:
        def __init__(self, db):
            self.db = db

        async def change_password(self, *, user_id: int, current_password: str, new_password: str):
            raise ValueError("Invalid current password")

    monkeypatch.setattr(router_module, "UserService", FakeService)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": "bad",
                "new_password": "newpass",
                "confirm_password": "newpass",
            },
        )

    assert resp.status_code == 400
    assert resp.json()["detail"] == "현재 비밀번호가 올바르지 않습니다."
