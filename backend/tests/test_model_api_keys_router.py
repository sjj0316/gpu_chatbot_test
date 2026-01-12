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
        self.code = code


class FakeUser:
    def __init__(self, user_id: int, role_code: str = "user") -> None:
        self.id = user_id
        self.role = FakeRole(role_code)


def _make_key(owner_id: int = 1, api_key: str = "secret") -> SimpleNamespace:
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
    async def override_db():
        yield None

    app.dependency_overrides[get_db] = override_db
    yield
    app.dependency_overrides.clear()


def _set_current_user(user: FakeUser) -> None:
    def override_user():
        return user

    app.dependency_overrides[get_current_user] = override_user


@pytest.mark.asyncio
async def test_list_model_keys_owner_override_for_non_admin(monkeypatch: pytest.MonkeyPatch):
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

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.get("/api/v1/api-keys?owner_id=999")

    assert resp.status_code == 200
    assert received["owner_id"] == 1


@pytest.mark.asyncio
async def test_get_model_key_forbidden_reveal_secret_non_owner(
    monkeypatch: pytest.MonkeyPatch,
):
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

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.get("/api/v1/api-keys/1?reveal_secret=true")

    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_get_model_key_owner_can_reveal_secret(monkeypatch: pytest.MonkeyPatch):
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

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.get("/api/v1/api-keys/1?reveal_secret=true")

    assert resp.status_code == 200
    assert resp.json()["api_key"] == "shhh"


@pytest.mark.asyncio
async def test_create_model_key_conflict(monkeypatch: pytest.MonkeyPatch):
    class FakeService:
        def __init__(self, session):
            self.session = session

        async def create(self, owner_id: int, payload):
            raise ValueError("duplicate")

    monkeypatch.setattr(router_module, "ModelApiKeyService", FakeService)
    _set_current_user(FakeUser(1, "user"))

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

    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_update_model_key_forbidden_non_owner(
    monkeypatch: pytest.MonkeyPatch,
):
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

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.patch("/api/v1/api-keys/1", json={"alias": "new"})

    assert resp.status_code == 403
    assert called["update"] is False


@pytest.mark.asyncio
async def test_delete_model_key_not_found(monkeypatch: pytest.MonkeyPatch):
    class FakeService:
        def __init__(self, session):
            self.session = session

        async def get(self, key_id: int):
            return None

    monkeypatch.setattr(router_module, "ModelApiKeyService", FakeService)
    _set_current_user(FakeUser(1, "user"))

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.delete("/api/v1/api-keys/123")

    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_model_keys_admin_can_query_other_owner(
    monkeypatch: pytest.MonkeyPatch,
):
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

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.get("/api/v1/api-keys?owner_id=999")

    assert resp.status_code == 200
    assert received["owner_id"] == 999


@pytest.mark.asyncio
async def test_get_model_key_admin_can_reveal_secret(monkeypatch: pytest.MonkeyPatch):
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

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.get("/api/v1/api-keys/1?reveal_secret=true")

    assert resp.status_code == 200
    assert resp.json()["api_key"] == "admin-secret"


@pytest.mark.asyncio
async def test_update_model_key_admin_can_update(monkeypatch: pytest.MonkeyPatch):
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

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.patch("/api/v1/api-keys/1", json={"alias": "new"})

    assert resp.status_code == 200
    assert called["update"] is True


@pytest.mark.asyncio
async def test_delete_model_key_admin_can_delete(monkeypatch: pytest.MonkeyPatch):
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

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.delete("/api/v1/api-keys/1")

    assert resp.status_code == 204
    assert called["delete"] is True
