from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.dependencies.auth import get_current_user
from app.services.chat import ChatService
from app.utils import create_access_token


class FakeRole:
    def __init__(self, code: str) -> None:
        self.code = code


class FakeUser:
    def __init__(self, user_id: int, username: str, role_code: str = "user") -> None:
        self.id = user_id
        self.username = username
        self.role = FakeRole(role_code)


class _Result:
    def __init__(self, obj=None, items=None) -> None:
        self._obj = obj
        self._items = items or []

    def scalar_one(self):
        return self._obj

    def scalar_one_or_none(self):
        return self._obj

    def scalars(self):
        return self._items


@pytest.mark.asyncio
async def test_get_model_key_denies_private_key_for_other_user():
    # token -> current_user 생성
    token = create_access_token({"sub": "user_a"})
    fake_db = MagicMock()
    fake_db.execute = AsyncMock(
        return_value=_Result(FakeUser(1, "user_a", "user"))
    )
    user = await get_current_user(token=f"Bearer {token}", db=fake_db)

    # private key(owner_id=2) 접근 차단
    model_key = SimpleNamespace(is_public=False, owner_id=2, id=10)
    session = MagicMock()
    session.execute = AsyncMock(return_value=_Result(model_key))
    chat = ChatService(session)
    conv = SimpleNamespace(default_model_key_id=10)

    with pytest.raises(HTTPException) as exc:
        await chat._get_model_key(
            explicit_model_key_id=None,
            conversation=conv,
            user=user,
        )

    assert exc.value.status_code == 403
    assert session.execute.call_count == 1


@pytest.mark.asyncio
async def test_get_mcp_servers_denies_private_server_for_other_user():
    token = create_access_token({"sub": "user_a"})
    fake_db = MagicMock()
    fake_db.execute = AsyncMock(
        return_value=_Result(FakeUser(1, "user_a", "user"))
    )
    user = await get_current_user(token=f"Bearer {token}", db=fake_db)

    session = MagicMock()
    session.execute = AsyncMock(return_value=_Result(items=[]))
    chat = ChatService(session)

    with pytest.raises(HTTPException) as exc:
        await chat._get_mcp_servers([5], user=user)

    assert exc.value.status_code == 403
