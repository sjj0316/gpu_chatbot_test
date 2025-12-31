import pytest
import asyncio
from httpx import AsyncClient

from app.main import app

@pytest.mark.asyncio
async def test_root():
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        r = await ac.get("/")
        assert r.status_code == 200
        assert r.json().get("message") == "Hello, FastAPI!"

@pytest.mark.asyncio
async def test_openapi():
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        r = await ac.get("/openapi.json")
        assert r.status_code == 200
        data = r.json()
        assert "paths" in data

@pytest.mark.asyncio
async def test_get_mcp_servers():
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        r = await ac.get("/api/v1/mcp-servers")
        # endpoint should respond (may return empty list)
        assert r.status_code in (200, 204)
        if r.status_code == 200:
            assert isinstance(r.json(), list)
