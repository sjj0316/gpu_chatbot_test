from __future__ import annotations

import os
from uuid import uuid4

import pytest

from .conftest import async_client, auth_header, login


def _get_env_key(*names: str) -> str | None:
    # 여러 환경 변수 후보 중 먼저 설정된 값을 반환한다.
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return None


@pytest.mark.asyncio
async def test_admin_can_register_env_model_keys(async_client):
    # 통합 테스트는 실제 키를 쓰므로 환경 변수가 없으면 스킵한다.
    test_key = _get_env_key("TEST_API_Key", "TEST_API_KEY")
    embedding_key = _get_env_key("EMBEDDING_KEY", "EMBEDDINGS_KEY")
    if not test_key or not embedding_key:
        pytest.skip("Required env keys not provided for API key tests.")

    # 관리자 계정으로 API 키를 등록하고 목록에서 확인한다.
    admin_token = await login(async_client, "admin", "data123!")
    headers = auth_header(admin_token)

    alias_chat = f"test-chat-{uuid4().hex[:8]}"
    alias_embed = f"test-embed-{uuid4().hex[:8]}"

    created_ids: list[int] = []
    try:
        chat_resp = await async_client.post(
            "/api/v1/api-keys",
            headers=headers,
            json={
                "alias": alias_chat,
                "provider_code": "openai",
                "model": "gpt-4o-mini",
                "endpoint_url": None,
                "purpose_code": "chat",
                "api_key": test_key,
                "is_public": False,
                "is_active": True,
            },
        )
        chat_resp.raise_for_status()
        created_ids.append(chat_resp.json()["id"])

        embed_resp = await async_client.post(
            "/api/v1/api-keys",
            headers=headers,
            json={
                "alias": alias_embed,
                "provider_code": "openai",
                "model": "text-embedding-3-small",
                "endpoint_url": None,
                "purpose_code": "embedding",
                "api_key": embedding_key,
                "is_public": False,
                "is_active": True,
            },
        )
        embed_resp.raise_for_status()
        created_ids.append(embed_resp.json()["id"])

        listed = await async_client.get("/api/v1/api-keys", headers=headers)
        listed.raise_for_status()
        aliases = {item["alias"] for item in listed.json()}
        assert alias_chat in aliases
        assert alias_embed in aliases
    finally:
        for key_id in created_ids:
            await async_client.delete(f"/api/v1/api-keys/{key_id}", headers=headers)
