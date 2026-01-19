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
    # 통합 테스트에서 사용할 ASGI 클라이언트를 세션 단위로 재사용한다.
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest_asyncio.fixture(scope="session", autouse=True)
async def _normalize_system_user_email() -> None:
    # system 계정 이메일이 비어있거나 형식이 틀리면 로그인 테스트가 실패하므로 보정한다.
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
    # 로그인 API를 호출해 액세스 토큰을 반환한다.
    resp = await client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    resp.raise_for_status()
    data = resp.json()
    return data["access_token"]


def auth_header(token: str) -> dict[str, str]:
    # 인증이 필요한 요청에 사용할 Authorization 헤더를 구성한다.
    return {"Authorization": f"Bearer {token}"}


def database_url() -> str:
    # asyncpg가 이해할 수 있는 형태로 DATABASE_URL을 변환한다.
    url = os.environ.get("DATABASE_URL", "")
    if url.startswith("postgresql+asyncpg://"):
        return url.replace("postgresql+asyncpg://", "postgresql://", 1)
    return url
