from __future__ import annotations

import uuid

import pytest

from .conftest import async_client, auth_header, login


@pytest.mark.asyncio
async def test_authz_roles(async_client):
    resp = await async_client.get("/api/v1/collections/")
    assert resp.status_code == 403

    username = f"user_{uuid.uuid4().hex[:8]}"
    await async_client.post(
        "/api/v1/users",
        json={
            "username": username,
            "password": "userpass123!",
            "nickname": "Tester",
            "email": f"{username}@example.com",
        },
    )

    user_token = await login(async_client, username, "userpass123!")
    resp = await async_client.get("/api/v1/users", headers=auth_header(user_token))
    assert resp.status_code == 403

    admin_token = await login(async_client, "admin", "data123!")
    resp = await async_client.get("/api/v1/users", headers=auth_header(admin_token))
    assert resp.status_code == 200
