from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.security.authz import (
    get_mcp_server_authorized,
    get_mcp_servers_authorized,
    get_model_key_authorized,
)


class FakeRole:
    def __init__(self, code: str) -> None:
        self.code = code


class FakeUser:
    def __init__(self, user_id: int, role_code: str = "user") -> None:
        self.id = user_id
        self.role = FakeRole(role_code)


class _Result:
    def __init__(self, obj=None, items=None):
        self._obj = obj
        self._items = items or []

    def scalar_one_or_none(self):
        return self._obj

    def scalar_one(self):
        return self._obj

    def scalars(self):
        return self._items


@pytest.mark.asyncio
async def test_get_mcp_server_authorized_missing_returns_404():
    session = MagicMock()
    session.execute = AsyncMock(return_value=_Result(None))

    with pytest.raises(HTTPException) as exc:
        await get_mcp_server_authorized(session, 123, FakeUser(1))

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_get_mcp_servers_authorized_partial_denied_returns_403():
    session = MagicMock()
    session.execute = AsyncMock(
        return_value=_Result(
            items=[SimpleNamespace(id=1, is_public=True, owner_id=1)]
        )
    )

    with pytest.raises(HTTPException) as exc:
        await get_mcp_servers_authorized(session, [1, 2], FakeUser(1))

    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_get_model_key_authorized_two_phase_loading():
    session = MagicMock()
    obj1 = SimpleNamespace(id=1, is_public=True, owner_id=1)
    obj2 = SimpleNamespace(id=1, is_public=True, owner_id=1, api_key="secret")
    session.execute = AsyncMock(side_effect=[_Result(obj1), _Result(obj2)])

    obj = await get_model_key_authorized(session, 1, FakeUser(1))

    assert session.execute.call_count == 2
    assert getattr(obj, "api_key", None) == "secret"
