import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app

@pytest.mark.asyncio
async def test_root():
    # 실행: 루트 엔드포인트 호출.
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as ac:
        r = await ac.get("/")
        # 검증: 루트가 간단한 인사 페이로드 반환.
        assert r.status_code == 200
        assert r.json().get("message") == "Hello, FastAPI!"

@pytest.mark.asyncio
async def test_openapi():
    # 실행: OpenAPI 스키마 조회.
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as ac:
        r = await ac.get("/openapi.json")
        # 검증: 스키마에 paths 포함.
        assert r.status_code == 200
        data = r.json()
        assert "paths" in data

@pytest.mark.asyncio
async def test_get_mcp_servers():
    # 실행: 인증 가정 없이 MCP 서버 엔드포인트 호출.
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as ac:
        r = await ac.get("/api/v1/mcp-servers")
        # 엔드포인트는 응답해야 함(인증 필요할 수 있음)
        # 검증: 인증 요구에 따라 여러 상태 코드를 허용.
        assert r.status_code in (200, 204, 401, 403)
        if r.status_code == 200:
            # 검증: 성공 응답은 리스트 반환.
            assert isinstance(r.json(), list)
