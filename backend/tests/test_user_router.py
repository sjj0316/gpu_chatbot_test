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
    # 실 DB 접근을 피하려고 DB 의존성 오버라이드.
    async def override_db():
        yield None

    app.dependency_overrides[get_db] = override_db
    yield
    # 다른 테스트 영향 방지를 위해 오버라이드 정리.
    app.dependency_overrides.clear()


class FakeRole:
    def __init__(self, code: str) -> None:
        # current-user 의존성에서 쓰는 최소 Role 객체.
        self.code = code


class FakeUser:
    def __init__(self, user_id: int, role_code: str = "user") -> None:
        # get_current_user가 반환하는 최소 User 객체.
        self.id = user_id
        self.role = FakeRole(role_code)


def _set_current_user(user: FakeUser) -> None:
    # 테스트에서 역할을 시뮬레이션하도록 인증 의존성 오버라이드.
    def override_user():
        return user

    app.dependency_overrides[get_current_user] = override_user


@pytest.mark.asyncio
async def test_register_user_success(monkeypatch: pytest.MonkeyPatch):
    # 준비: 새 사용자 DTO를 반환하는 가짜 서비스 생성.
    created = SimpleNamespace(
        id=1, username="tester", nickname="Tester", email="test@example.com"
    )

    class FakeService:
        def __init__(self, db):
            self.db = db

        async def create_user(self, user_data):
            return created

    monkeypatch.setattr(router_module, "UserService", FakeService)

    # 실행: 회원가입 엔드포인트 호출.
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

    # 검증: 응답 페이로드가 유효하고 새 사용자명이 포함됨.
    assert resp.status_code == 201
    assert UserRead(**resp.json()).username == "tester"


@pytest.mark.asyncio
async def test_register_user_duplicate_username(monkeypatch: pytest.MonkeyPatch):
    # 준비: 사용자명 중복 오류를 내는 가짜 서비스.
    class FakeService:
        def __init__(self, db):
            self.db = db

        async def create_user(self, user_data):
            raise ValueError("Username already exists")

    monkeypatch.setattr(router_module, "UserService", FakeService)

    # 실행: 중복 사용자명으로 엔드포인트 호출.
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

    # 검증: 409 충돌 응답.
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_register_user_duplicate_email(monkeypatch: pytest.MonkeyPatch):
    # 준비: 이메일 중복 오류를 내는 가짜 서비스.
    class FakeService:
        def __init__(self, db):
            self.db = db

        async def create_user(self, user_data):
            raise ValueError("Email already exists")

    monkeypatch.setattr(router_module, "UserService", FakeService)

    # 실행: 중복 이메일로 엔드포인트 호출.
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

    # 검증: 409 충돌 응답.
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_register_user_missing_default_role(monkeypatch: pytest.MonkeyPatch):
    # 준비: 기본 역할 없음 오류를 내는 가짜 서비스.
    class FakeService:
        def __init__(self, db):
            self.db = db

        async def create_user(self, user_data):
            raise ValueError("Default user role not found")

    monkeypatch.setattr(router_module, "UserService", FakeService)

    # 실행: 409가 나와야 하는 엔드포인트 호출.
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

    # 검증: 기본 역할 없음이 409로 매핑.
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_list_users_admin_only(monkeypatch: pytest.MonkeyPatch):
    # 준비: 관리자에게 사용자 목록을 반환하는 가짜 서비스.
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

    # 실행: 관리자가 사용자 목록 요청.
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.get("/api/v1/users")

    # 검증: 사용자 목록 반환 및 스키마 파싱.
    assert resp.status_code == 200
    assert [UserRead(**item).username for item in resp.json()] == ["admin", "user"]


@pytest.mark.asyncio
async def test_list_users_forbidden_for_non_admin():
    # 준비: 비관리자 사용자 설정.
    _set_current_user(FakeUser(1, "user"))

    # 실행: 비관리자가 사용자 목록 요청.
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.get("/api/v1/users")

    # 검증: 접근 금지.
    assert resp.status_code == 403
