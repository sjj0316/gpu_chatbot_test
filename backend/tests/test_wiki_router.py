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
        # 인증 의존성을 위한 최소 User 객체.
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
    # 테스트 격리를 위해 오버라이드 초기화.
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_wiki_page_not_found(monkeypatch: pytest.MonkeyPatch):
    # 준비: 페이지 없음에 대해 None 반환하는 가짜 서비스.
    class FakeService:
        def __init__(self, db):
            self.db = db

        async def get_page(self, slug: str):
            return None

    monkeypatch.setattr(router_module, "WikiService", FakeService)

    # 실행: 존재하지 않는 페이지 요청.
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.get("/api/v1/wiki/guide")

    # 검증: 404 응답.
    assert resp.status_code == 404
    assert resp.json()["detail"] == "페이지를 찾을 수 없습니다."


@pytest.mark.asyncio
async def test_get_wiki_page_success(monkeypatch: pytest.MonkeyPatch):
    # 준비: 내용이 있는 위키 페이지를 반환하는 가짜 서비스.
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

    # 실행: 위키 페이지 요청.
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.get("/api/v1/wiki/guide")

    # 검증: 페이지 데이터 반환.
    assert resp.status_code == 200
    assert resp.json()["title"] == "사용 가이드"


@pytest.mark.asyncio
async def test_upsert_wiki_page(monkeypatch: pytest.MonkeyPatch):
    # 준비: 현재 사용자 설정 및 업서트 응답 스텁.
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

    # 실행: 위키 페이지 업서트.
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.put(
            "/api/v1/wiki/guide",
            json={"title": "문서", "content": "본문"},
        )

    # 검증: 업서트 결과 제목 확인.
    assert resp.status_code == 200
    assert resp.json()["title"] == "문서"
