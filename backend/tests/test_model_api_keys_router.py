from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.dependencies import get_db, get_current_user
from app.schemas import ModelApiKeyRead, ModelApiKeyReadWithSecret
from app.routers import model_api_keys as router_module


class FakeRole:
    def __init__(self, code: str) -> None:
        # 인가 체크를 위한 최소 Role 객체.
        self.code = code


class FakeUser:
    def __init__(self, user_id: int, role_code: str = "user") -> None:
        # get_current_user가 반환하는 최소 User 객체.
        self.id = user_id
        self.role = FakeRole(role_code)


def _make_key(owner_id: int = 1, api_key: str = "secret") -> SimpleNamespace:
    # 일관된 가짜 모델 API 키 레코드 생성.
    return SimpleNamespace(
        id=1,
        alias="test-key",
        provider_id=10,
        provider_code="openai",
        model="gpt-4o",
        endpoint_url=None,
        purpose_id=20,
        purpose_code="chat",
        is_public=False,
        is_active=True,
        extra=None,
        owner_id=owner_id,
        owner_nickname="tester",
        created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        updated_at=None,
        api_key_masked="***",
        api_key=api_key,
    )


@pytest.fixture(autouse=True)
def _override_db() -> None:
    # 라우터 테스트에서 실 DB 접근 회피.
    async def override_db():
        yield None

    app.dependency_overrides[get_db] = override_db
    yield
    # 각 테스트 후 오버라이드 정리.
    app.dependency_overrides.clear()


def _set_current_user(user: FakeUser) -> None:
    # 현재 사용자 역할을 설정하도록 인증 의존성 오버라이드.
    def override_user():
        return user

    app.dependency_overrides[get_current_user] = override_user


@pytest.mark.asyncio
async def test_list_model_keys_owner_override_for_non_admin(monkeypatch: pytest.MonkeyPatch):
    # 준비: 가짜 서비스가 owner_id를 기록하고 키 1개 반환.
    received: dict[str, int] = {}
    data = _make_key(owner_id=1)

    class FakeService:
        def __init__(self, session):
            self.session = session

        async def get_list(self, *, owner_id, **kwargs):
            received["owner_id"] = owner_id
            return [data], 1

        def to_read(self, obj, reveal_secret: bool = False):
            payload = obj.__dict__.copy()
            payload.pop("api_key", None)
            return ModelApiKeyRead(**payload)

    monkeypatch.setattr(router_module, "ModelApiKeyService", FakeService)
    _set_current_user(FakeUser(1, "user"))

    # 실행: 비관리자가 다른 소유자 키 조회 시도.
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.get("/api/v1/api-keys?owner_id=999")

    # 검증: owner_id가 현재 사용자로 강제됨.
    assert resp.status_code == 200
    assert received["owner_id"] == 1


@pytest.mark.asyncio
async def test_get_model_key_forbidden_reveal_secret_non_owner(
    monkeypatch: pytest.MonkeyPatch,
):
    # 준비: 키 소유자가 다른 사용자.
    data = _make_key(owner_id=2)

    class FakeService:
        def __init__(self, session):
            self.session = session

        async def get(self, key_id: int):
            return data

        def to_read(self, obj, reveal_secret: bool = False):
            payload = obj.__dict__.copy()
            if not reveal_secret:
                payload.pop("api_key", None)
            return (
                ModelApiKeyReadWithSecret(**payload)
                if reveal_secret
                else ModelApiKeyRead(**payload)
            )

    monkeypatch.setattr(router_module, "ModelApiKeyService", FakeService)
    _set_current_user(FakeUser(1, "user"))

    # 실행: 비소유자가 시크릿 공개 요청.
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.get("/api/v1/api-keys/1?reveal_secret=true")

    # 검증: 비소유자 접근 금지.
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_get_model_key_owner_can_reveal_secret(monkeypatch: pytest.MonkeyPatch):
    # 준비: 현재 사용자가 소유한 키.
    data = _make_key(owner_id=2, api_key="shhh")

    class FakeService:
        def __init__(self, session):
            self.session = session

        async def get(self, key_id: int):
            return data

        def to_read(self, obj, reveal_secret: bool = False):
            payload = obj.__dict__.copy()
            if not reveal_secret:
                payload.pop("api_key", None)
            return (
                ModelApiKeyReadWithSecret(**payload)
                if reveal_secret
                else ModelApiKeyRead(**payload)
            )

    monkeypatch.setattr(router_module, "ModelApiKeyService", FakeService)
    _set_current_user(FakeUser(2, "user"))

    # 실행: 소유자가 시크릿 공개 요청.
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.get("/api/v1/api-keys/1?reveal_secret=true")

    # 검증: 소유자에게 시크릿 반환.
    assert resp.status_code == 200
    assert resp.json()["api_key"] == "shhh"


@pytest.mark.asyncio
async def test_create_model_key_conflict(monkeypatch: pytest.MonkeyPatch):
    # 준비: 중복 생성 시 서비스 예외 발생.
    class FakeService:
        def __init__(self, session):
            self.session = session

        async def create(self, owner_id: int, payload):
            raise ValueError("duplicate")

    monkeypatch.setattr(router_module, "ModelApiKeyService", FakeService)
    _set_current_user(FakeUser(1, "user"))

    # 실행: 중복 키 생성 시도.
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.post(
            "/api/v1/api-keys",
            json={
                "alias": "test",
                "provider_code": "openai",
                "model": "gpt-4o",
                "endpoint_url": None,
                "purpose_code": "chat",
                "api_key": "secret",
                "is_public": False,
                "is_active": True,
            },
        )

    # 검증: 409 충돌 응답.
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_update_model_key_forbidden_non_owner(
    monkeypatch: pytest.MonkeyPatch,
):
    # 준비: 키 소유자가 다른 사람.
    data = _make_key(owner_id=2)
    called = {"update": False}

    class FakeService:
        def __init__(self, session):
            self.session = session

        async def get(self, key_id: int):
            return data

        async def update(self, obj, payload):
            called["update"] = True
            return data

        def to_read(self, obj, reveal_secret: bool = False):
            payload = obj.__dict__.copy()
            payload.pop("api_key", None)
            return ModelApiKeyReadWithSecret(**payload)

    monkeypatch.setattr(router_module, "ModelApiKeyService", FakeService)
    _set_current_user(FakeUser(1, "user"))

    # 실행: 비소유자 업데이트 시도.
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.patch("/api/v1/api-keys/1", json={"alias": "new"})

    # 검증: 금지 응답이며 update 미호출.
    assert resp.status_code == 403
    assert called["update"] is False


@pytest.mark.asyncio
async def test_delete_model_key_not_found(monkeypatch: pytest.MonkeyPatch):
    # 준비: 키 없음에 대해 서비스가 None 반환.
    class FakeService:
        def __init__(self, session):
            self.session = session

        async def get(self, key_id: int):
            return None

    monkeypatch.setattr(router_module, "ModelApiKeyService", FakeService)
    _set_current_user(FakeUser(1, "user"))

    # 실행: 존재하지 않는 키 삭제.
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.delete("/api/v1/api-keys/123")

    # 검증: 404 응답.
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_model_keys_admin_can_query_other_owner(
    monkeypatch: pytest.MonkeyPatch,
):
    # 준비: 관리자가 다른 소유자의 키 조회.
    received: dict[str, int] = {}
    data = _make_key(owner_id=2)

    class FakeService:
        def __init__(self, session):
            self.session = session

        async def get_list(self, *, owner_id, **kwargs):
            received["owner_id"] = owner_id
            return [data], 1

        def to_read(self, obj, reveal_secret: bool = False):
            payload = obj.__dict__.copy()
            payload.pop("api_key", None)
            return ModelApiKeyRead(**payload)

    monkeypatch.setattr(router_module, "ModelApiKeyService", FakeService)
    _set_current_user(FakeUser(1, "admin"))

    # 실행: 관리자가 다른 소유자 키 요청.
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.get("/api/v1/api-keys?owner_id=999")

    # 검증: 관리자는 요청한 owner_id 유지 가능.
    assert resp.status_code == 200
    assert received["owner_id"] == 999


@pytest.mark.asyncio
async def test_get_model_key_admin_can_reveal_secret(monkeypatch: pytest.MonkeyPatch):
    # 준비: 관리자가 타인 키의 시크릿 요청.
    data = _make_key(owner_id=2, api_key="admin-secret")

    class FakeService:
        def __init__(self, session):
            self.session = session

        async def get(self, key_id: int):
            return data

        def to_read(self, obj, reveal_secret: bool = False):
            payload = obj.__dict__.copy()
            if not reveal_secret:
                payload.pop("api_key", None)
            return (
                ModelApiKeyReadWithSecret(**payload)
                if reveal_secret
                else ModelApiKeyRead(**payload)
            )

    monkeypatch.setattr(router_module, "ModelApiKeyService", FakeService)
    _set_current_user(FakeUser(1, "admin"))

    # 실행: 관리자가 시크릿 공개.
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.get("/api/v1/api-keys/1?reveal_secret=true")

    # 검증: 관리자에게 시크릿 반환.
    assert resp.status_code == 200
    assert resp.json()["api_key"] == "admin-secret"


@pytest.mark.asyncio
async def test_update_model_key_admin_can_update(monkeypatch: pytest.MonkeyPatch):
    # 준비: 관리자가 다른 소유자 키 업데이트.
    data = _make_key(owner_id=2)
    called = {"update": False}

    class FakeService:
        def __init__(self, session):
            self.session = session

        async def get(self, key_id: int):
            return data

        async def update(self, obj, payload):
            called["update"] = True
            return data

        def to_read(self, obj, reveal_secret: bool = False):
            payload = obj.__dict__.copy()
            payload.pop("api_key", None)
            return ModelApiKeyReadWithSecret(**payload)

    monkeypatch.setattr(router_module, "ModelApiKeyService", FakeService)
    _set_current_user(FakeUser(1, "admin"))

    # 실행: 관리자가 키 별칭 업데이트.
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.patch("/api/v1/api-keys/1", json={"alias": "new"})

    # 검증: 관리자는 업데이트 허용.
    assert resp.status_code == 200
    assert called["update"] is True


@pytest.mark.asyncio
async def test_delete_model_key_admin_can_delete(monkeypatch: pytest.MonkeyPatch):
    # 준비: 관리자가 다른 소유자 키 삭제.
    data = _make_key(owner_id=2)
    called = {"delete": False}

    class FakeService:
        def __init__(self, session):
            self.session = session

        async def get(self, key_id: int):
            return data

        async def delete(self, obj):
            called["delete"] = True

    monkeypatch.setattr(router_module, "ModelApiKeyService", FakeService)
    _set_current_user(FakeUser(1, "admin"))

    # 실행: 관리자가 키 삭제.
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.delete("/api/v1/api-keys/1")

    # 검증: 삭제 성공 및 서비스 메서드 호출.
    assert resp.status_code == 204
    assert called["delete"] is True
