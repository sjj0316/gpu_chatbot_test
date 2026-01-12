from __future__ import annotations

import pytest

from .conftest import async_client, auth_header, login


@pytest.mark.asyncio
async def test_wiki_crud(async_client):
    admin_token = await login(async_client, "admin", "data123!")
    headers = auth_header(admin_token)

    update = await async_client.put(
        "/api/v1/wiki/guide",
        headers=headers,
        json={"title": "테스트 가이드", "content": "통합 테스트 내용"},
    )
    update.raise_for_status()
    assert update.json()["title"] == "테스트 가이드"

    fetch = await async_client.get("/api/v1/wiki/guide", headers=headers)
    fetch.raise_for_status()
    assert fetch.json()["content"] == "통합 테스트 내용"
