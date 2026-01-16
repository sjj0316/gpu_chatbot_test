from __future__ import annotations

import os
from typing import AsyncGenerator

import pytest
import pytest_asyncio
import asyncpg
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest_asyncio.fixture(scope="session")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest_asyncio.fixture(scope="session", autouse=True)
async def _normalize_system_user_email() -> None:
    url = database_url()
    if not url:
        return
    conn = await asyncpg.connect(url)
    try:
        await conn.execute(
            """
            UPDATE users
            SET email = 'system@example.com'
            WHERE username = 'system'
              AND (email IS NULL OR email NOT LIKE '%@%.%')
            """
        )
    finally:
        await conn.close()


async def login(client: AsyncClient, username: str, password: str) -> str:
    resp = await client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    resp.raise_for_status()
    data = resp.json()
    return data["access_token"]


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def database_url() -> str:
    url = os.environ.get("DATABASE_URL", "")
    if url.startswith("postgresql+asyncpg://"):
        return url.replace("postgresql+asyncpg://", "postgresql://", 1)
    return url
