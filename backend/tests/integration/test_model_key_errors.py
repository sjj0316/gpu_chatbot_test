from __future__ import annotations

import pytest

from .conftest import async_client, auth_header, login


@pytest.mark.asyncio
async def test_model_key_invalid_provider(async_client):
    admin_token = await login(async_client, "admin", "data123!")
    headers = auth_header(admin_token)

    resp = await async_client.post(
        "/api/v1/api-keys",
        headers=headers,
        json={
            "alias": "bad-provider",
            "provider_code": "no-such-provider",
            "purpose_code": "embedding",
            "model": "text-embedding-3-small",
            "api_key": "dummy",
            "is_public": False,
            "is_active": True,
        },
    )

    assert resp.status_code == 409
