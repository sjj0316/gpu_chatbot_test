from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.schemas import MCPServerUpdate, MCPServerRuntime
from app.services.mcp_server import MCPServerService


class FakeRole:
    def __init__(self, code: str) -> None:
        self.code = code


class FakeUser:
    def __init__(self, user_id: int, role_code: str = "user") -> None:
        self.id = user_id
        self.role = FakeRole(role_code)


def _make_server(owner_id: int, is_public: bool = False) -> SimpleNamespace:
    return SimpleNamespace(
        id=1,
        name="Demo MCP",
        description="test",
        config={"transport": "http", "url": "http://localhost:9000"},
        is_public=is_public,
        owner_id=owner_id,
    )


@pytest.mark.asyncio
async def test_get_mcp_server_denied_for_private_non_owner(monkeypatch: pytest.MonkeyPatch):
    session = MagicMock()
    session.get = AsyncMock(return_value=_make_server(owner_id=2, is_public=False))

    service = MCPServerService(session)
    with pytest.raises(HTTPException) as exc:
        await service.get(1, user=FakeUser(1, "user"))

    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_get_mcp_server_allows_public(monkeypatch: pytest.MonkeyPatch):
    session = MagicMock()
    session.get = AsyncMock(return_value=_make_server(owner_id=2, is_public=True))
    monkeypatch.setattr(
        "app.services.mcp_server.probe_mcp_server",
        AsyncMock(return_value=MCPServerRuntime(reachable=True, tools=[])),
    )

    service = MCPServerService(session)
    dto = await service.get(1, user=FakeUser(1, "user"))

    assert dto.id == 1
    assert dto.is_public is True


@pytest.mark.asyncio
async def test_update_mcp_server_denied_for_non_owner():
    session = MagicMock()
    session.get = AsyncMock(return_value=_make_server(owner_id=2, is_public=False))

    service = MCPServerService(session)
    with pytest.raises(HTTPException) as exc:
        await service.update(
            1,
            MCPServerUpdate(name="Updated"),
            user=FakeUser(1, "user"),
        )

    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_update_mcp_server_allows_admin(monkeypatch: pytest.MonkeyPatch):
    session = MagicMock()
    server = _make_server(owner_id=2, is_public=False)
    session.get = AsyncMock(return_value=server)
    session.scalar = AsyncMock(return_value=None)
    session.commit = AsyncMock()
    session.refresh = AsyncMock()

    service = MCPServerService(session)
    dto = await service.update(
        1,
        MCPServerUpdate(name="Updated", is_public=True),
        user=FakeUser(1, "admin"),
    )

    assert dto.name == "Updated"
    assert server.is_public is True
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_mcp_server_denied_for_non_owner():
    session = MagicMock()
    session.get = AsyncMock(return_value=_make_server(owner_id=2, is_public=False))

    service = MCPServerService(session)
    with pytest.raises(HTTPException) as exc:
        await service.delete(1, user=FakeUser(1, "user"))

    assert exc.value.status_code == 403
