from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.services import document as document_service
from .conftest import async_client, auth_header, login


class DummyEmbeddings:
    # 외부 임베딩 호출을 피하기 위한 더미 임베딩 구현.
    def embed_documents(self, texts):
        return [[0.0] * 1536 for _ in texts]

    def embed_query(self, text):
        return [0.0] * 1536

    async def aembed_documents(self, texts):
        return self.embed_documents(texts)

    async def aembed_query(self, text):
        return self.embed_query(text)


@pytest.mark.asyncio
async def test_rag_flow(async_client, monkeypatch: pytest.MonkeyPatch):
    # 문서 임베딩 의존성을 더미로 대체해 통합 테스트를 안정화한다.
    monkeypatch.setattr(
        document_service, "get_embedding", lambda model_name, model_api_key: DummyEmbeddings()
    )

    # 관리자 로그인 후 임베딩 키를 조회한다.
    admin_token = await login(async_client, "admin", "data123!")
    headers = auth_header(admin_token)

    keys = await async_client.get("/api/v1/api-keys", headers=headers)
    keys.raise_for_status()
    embedding_key = next(
        (k for k in keys.json() if k.get("purpose_code") == "embedding"),
        None,
    )
    assert embedding_key is not None

    # 컬렉션 생성 → 문서 업로드 → 검색 → 삭제의 흐름을 검증한다.
    resp = await async_client.post(
        "/api/v1/collections/",
        headers=headers,
        json={
            "name": "integration-collection",
            "description": "integration test",
            "is_public": False,
            "model_api_key_id": embedding_key["id"],
        },
    )
    resp.raise_for_status()
    collection_id = resp.json()["collection_id"]

    upload = await async_client.post(
        f"/api/v1/collections/{collection_id}/documents",
        headers=headers,
        files={"files": ("sample.txt", b"hello vector search", "text/plain")},
        data={"chunk_size": "200", "chunk_overlap": "20", "model_api_key_id": str(embedding_key["id"])},
    )
    upload.raise_for_status()

    search = await async_client.post(
        f"/api/v1/collections/{collection_id}/documents/search",
        headers=headers,
        json={"query": "hello", "limit": 5, "search_type": "keyword"},
    )
    search.raise_for_status()
    assert len(search.json()) >= 1

    # 문서/컬렉션을 정리해 다음 테스트에 영향을 주지 않도록 한다.
    deleted = await async_client.request(
        "DELETE",
        f"/api/v1/collections/{collection_id}/documents",
        headers=headers,
        json={},
    )
    assert deleted.status_code in (204, 404)

    cleanup = await async_client.delete(
        f"/api/v1/collections/{collection_id}",
        headers=headers,
    )
    assert cleanup.status_code == 204
