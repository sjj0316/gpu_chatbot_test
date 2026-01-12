from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.services import document as document_service
from .conftest import async_client, auth_header, login


class DummyEmbeddings:
    def embed_documents(self, texts):
        return [[0.0] * 1536 for _ in texts]

    def embed_query(self, text):
        return [0.0] * 1536


@pytest.mark.asyncio
async def test_rag_flow(async_client, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        document_service, "get_embedding", lambda model_name, model_api_key: DummyEmbeddings()
    )

    admin_token = await login(async_client, "admin", "data123!")
    headers = auth_header(admin_token)

    keys = await async_client.get("/api/v1/api-keys", headers=headers)
    keys.raise_for_status()
    embedding_key = next(
        (k for k in keys.json() if k.get("purpose_code") == "embedding"),
        None,
    )
    assert embedding_key is not None

    resp = await async_client.post(
        "/api/v1/collections/",
        headers=headers,
        json={
            "name": "통합 테스트 컬렉션",
            "description": "통합 테스트",
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
        json={"query": "hello", "limit": 5, "search_type": "semantic"},
    )
    search.raise_for_status()
    assert len(search.json()) >= 1

    deleted = await async_client.delete(
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
