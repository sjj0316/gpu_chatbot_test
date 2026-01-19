from __future__ import annotations

from types import SimpleNamespace

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.dependencies import get_db, get_current_user
from app.routers import auth as router_module


class FakeUser:
    def __init__(self, user_id: int) -> None:
        # 인증 라우트용 최소 User 객체.
        self.id = user_id


def _set_current_user(user: FakeUser) -> None:
    # 로그인 사용자를 시뮬레이션하도록 인증 의존성 오버라이드.
    def override_user():
        return user

    app.dependency_overrides[get_current_user] = override_user


@pytest.fixture(autouse=True)
def _override_db() -> None:
    # 의존성 오버라이드로 실 DB 접근 회피.
    async def override_db():
        yield None

    app.dependency_overrides[get_db] = override_db
    yield
    # 다른 테스트에 영향 없도록 오버라이드 초기화.
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_login_invalid_credentials(monkeypatch: pytest.MonkeyPatch):
    # 준비: 인증 실패를 나타내도록 auth 서비스가 None 반환.
    class FakeService:
        def __init__(self, db):
            self.db = db

        async def authenticate_user(self, login_data):
            return None

    monkeypatch.setattr(router_module, "AuthService", FakeService)

    # 실행: 잘못된 자격 증명으로 로그인 시도.
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.post(
            "/api/v1/auth/login",
            json={"username": "tester", "password": "wrong"},
        )

    # 검증: 기대 메시지와 함께 401 응답.
    assert resp.status_code == 401
    assert resp.json()["detail"] == "아이디 또는 비밀번호가 올바르지 않습니다."


@pytest.mark.asyncio
async def test_change_password_mismatch():
    # 준비: 현재 사용자 설정 후 새 비밀번호/확인 비밀번호 불일치 전송.
    _set_current_user(FakeUser(1))

    # 실행: 불일치 필드로 change-password 호출.
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

    # 검증: 검증 오류 응답.
    assert resp.status_code == 400
    assert resp.json()["detail"] == "새 비밀번호가 일치하지 않습니다."


@pytest.mark.asyncio
async def test_change_password_same_as_current():
    # 준비: 현재 사용자 설정 후 동일 비밀번호 재사용.
    _set_current_user(FakeUser(1))

    # 실행: 현재/새 비밀번호가 동일하게 change-password 호출.
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

    # 검증: 동일 비밀번호 거부.
    assert resp.status_code == 400
    assert resp.json()["detail"] == "새 비밀번호는 현재 비밀번호와 달라야 합니다."


@pytest.mark.asyncio
async def test_change_password_invalid_current(monkeypatch: pytest.MonkeyPatch):
    # 준비: 현재 비밀번호를 거부하는 가짜 서비스와 사용자 설정.
    _set_current_user(FakeUser(1))

    class FakeService:
        def __init__(self, db):
            self.db = db

        async def change_password(self, *, user_id: int, current_password: str, new_password: str):
            raise ValueError("Invalid current password")

    monkeypatch.setattr(router_module, "UserService", FakeService)

    # 실행: 잘못된 현재 비밀번호로 change-password 호출.
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

    # 검증: 검증 오류가 노출됨.
    assert resp.status_code == 400
    assert resp.json()["detail"] == "현재 비밀번호가 올바르지 않습니다."
