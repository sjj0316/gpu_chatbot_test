from __future__ import annotations

from types import SimpleNamespace
from uuid import UUID

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.dependencies import get_db, get_current_user
from app.routers import rag as router_module


class FakeRole:
    def __init__(self, code: str) -> None:
        # 인가 로직을 위한 최소 Role 객체.
        self.code = code


class FakeUser:
    def __init__(self, user_id: int, role_code: str = "user") -> None:
        # get_current_user가 반환하는 최소 User 객체.
        self.id = user_id
        self.role = FakeRole(role_code)


def _set_current_user(user: FakeUser) -> None:
    # 로그인 사용자를 시뮬레이션하도록 인증 의존성 오버라이드.
    def override_user():
        return user

    app.dependency_overrides[get_current_user] = override_user


@pytest.fixture(autouse=True)
def _override_db() -> None:
    # 실 DB 호출을 피하려고 DB 의존성을 오버라이드.
    async def override_db():
        yield None

    app.dependency_overrides[get_db] = override_db
    yield
    # 각 테스트 후 오버라이드를 정리.
    app.dependency_overrides.clear()


def _collection_read():
    # 테스트 전반에서 쓰는 표준 컬렉션 페이로드 반환.
    return {
        "collection_id": str(UUID("00000000-0000-0000-0000-000000000001")),
        "table_id": "collection_00000000_0000_0000_0000_000000000001",
        "name": "테스트 컬렉션",
        "description": "설명",
        "embedding_id": 1,
        "embedding_dimension": 1536,
        "embedding_model": "text-embedding-3-small",
        "is_public": False,
        "owner_id": 1,
        "document_count": 0,
        "chunk_count": 0,
    }


@pytest.mark.asyncio
async def test_create_collection(monkeypatch: pytest.MonkeyPatch):
    # 준비: 현재 사용자 설정 및 컬렉션 서비스 스텁.
    _set_current_user(FakeUser(1))

    class FakeService:
        def __init__(self, db):
            self.db = db

        async def create(self, user, data):
            return _collection_read()

    monkeypatch.setattr(router_module, "CollectionService", FakeService)

    # 실행: API로 컬렉션 생성 요청.
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.post(
            "/api/v1/collections/",
            json={
                "name": "테스트 컬렉션",
                "description": "설명",
                "is_public": False,
                "model_api_key_id": 1,
            },
        )

    # 검증: 생성 결과 페이로드가 기대값.
    assert resp.status_code == 201
    assert resp.json()["name"] == "테스트 컬렉션"


@pytest.mark.asyncio
async def test_list_collections(monkeypatch: pytest.MonkeyPatch):
    # 준비: 현재 사용자 설정 및 목록 응답 스텁.
    _set_current_user(FakeUser(1))

    class FakeService:
        def __init__(self, db):
            self.db = db

        async def get_list(self, user, *, limit: int, offset: int):
            return {"total_count": 1, "items": [_collection_read()]}

    monkeypatch.setattr(router_module, "CollectionService", FakeService)

    # 실행: 컬렉션 목록 요청.
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.get("/api/v1/collections/")

    # 검증: 목록 응답에 기대 항목 포함.
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["total_count"] == 1
    assert payload["items"][0]["name"] == "테스트 컬렉션"


@pytest.mark.asyncio
async def test_upload_document(monkeypatch: pytest.MonkeyPatch):
    # 준비: 현재 사용자 설정 및 문서 ingest 응답 스텁.
    _set_current_user(FakeUser(1))

    class FakeService:
        def __init__(self, db, collection_id, user):
            self.db = db

        async def create(self, files, metadatas, chunk_size, chunk_overlap, model_api_key_id):
            return SimpleNamespace(
                success=True,
                message="업로드 완료",
                added_chunk_ids=["c1"],
                warnings=None,
            )

    monkeypatch.setattr(router_module, "DocumentService", FakeService)

    # 실행: 컬렉션에 문서 업로드.
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        resp = await ac.post(
            "/api/v1/collections/00000000-0000-0000-0000-000000000001/documents",
            files={"files": ("test.txt", b"hello", "text/plain")},
            data={
                "chunk_size": "1000",
                "chunk_overlap": "200",
                "model_api_key_id": "1",
            },
        )

    # 검증: 업로드 성공 표시.
    assert resp.status_code == 201
    assert resp.json()["success"] is True
