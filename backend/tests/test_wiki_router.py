from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.dependencies import get_db, get_current_user
from app.routers import wiki as router_module


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
async def test_get_wiki_page_not_found(monkeypatch: pytest.MonkeyPatch):
    class FakeService:
        def __init__(self, db):
            self.db = db

        async def get_page(self, slug: str):
            return None

    monkeypatch.setattr(router_module, "WikiService", FakeService)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.get("/api/v1/wiki/guide")

    assert resp.status_code == 404
    assert resp.json()["detail"] == "페이지를 찾을 수 없습니다."


@pytest.mark.asyncio
async def test_get_wiki_page_success(monkeypatch: pytest.MonkeyPatch):
    class FakeService:
        def __init__(self, db):
            self.db = db

        async def get_page(self, slug: str):
            return SimpleNamespace(
                slug=slug,
                title="사용 가이드",
                content="내용",
                updated_at=datetime(2026, 1, 9, tzinfo=timezone.utc),
                updated_by="admin",
            )

    monkeypatch.setattr(router_module, "WikiService", FakeService)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.get("/api/v1/wiki/guide")

    assert resp.status_code == 200
    assert resp.json()["title"] == "사용 가이드"


@pytest.mark.asyncio
async def test_upsert_wiki_page(monkeypatch: pytest.MonkeyPatch):
    _set_current_user(FakeUser(1))

    class FakeService:
        def __init__(self, db):
            self.db = db

        async def upsert_page(self, slug: str, payload, *, user):
            return SimpleNamespace(
                slug=slug,
                title=payload.title or "기본",
                content=payload.content,
                updated_at=None,
                updated_by="tester",
            )

    monkeypatch.setattr(router_module, "WikiService", FakeService)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.put(
            "/api/v1/wiki/guide",
            json={"title": "문서", "content": "본문"},
        )

    assert resp.status_code == 200
    assert resp.json()["title"] == "문서"
