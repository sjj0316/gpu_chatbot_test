from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.schemas.user import UserCreate
from app.services.user import UserService


@pytest.mark.asyncio
async def test_create_user_success(monkeypatch: pytest.MonkeyPatch):
    session = MagicMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.add = MagicMock()

    username_result = MagicMock()
    username_result.scalar_one_or_none.return_value = None
    email_result = MagicMock()
    email_result.scalar_one_or_none.return_value = None
    role_result = MagicMock()
    role_result.scalar_one_or_none.return_value = 2
    session.execute.side_effect = [username_result, email_result, role_result]

    monkeypatch.setattr("app.services.user.hash_password", lambda pw: "hashed")

    service = UserService(session)
    payload = UserCreate(
        username="tester",
        password="password123",
        nickname="Tester",
        email="test@example.com",
    )
    user = await service.create_user(payload)

    session.add.assert_called_once()
    added_user = session.add.call_args[0][0]
    assert user == added_user
    assert added_user.role_id == 2
    assert added_user.password == "hashed"
    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once_with(added_user)


@pytest.mark.asyncio
async def test_create_user_duplicate_username():
    session = MagicMock()
    session.execute = AsyncMock()

    username_result = MagicMock()
    username_result.scalar_one_or_none.return_value = SimpleNamespace()
    session.execute.return_value = username_result

    service = UserService(session)
    payload = UserCreate(
        username="tester",
        password="password123",
        nickname="Tester",
        email="test@example.com",
    )

    with pytest.raises(ValueError, match="Username already exists"):
        await service.create_user(payload)


@pytest.mark.asyncio
async def test_create_user_duplicate_email():
    session = MagicMock()
    session.execute = AsyncMock()

    username_result = MagicMock()
    username_result.scalar_one_or_none.return_value = None
    email_result = MagicMock()
    email_result.scalar_one_or_none.return_value = SimpleNamespace()
    session.execute.side_effect = [username_result, email_result]

    service = UserService(session)
    payload = UserCreate(
        username="tester",
        password="password123",
        nickname="Tester",
        email="test@example.com",
    )

    with pytest.raises(ValueError, match="Email already exists"):
        await service.create_user(payload)


@pytest.mark.asyncio
async def test_create_user_role_missing():
    session = MagicMock()
    session.execute = AsyncMock()

    username_result = MagicMock()
    username_result.scalar_one_or_none.return_value = None
    email_result = MagicMock()
    email_result.scalar_one_or_none.return_value = None
    role_result = MagicMock()
    role_result.scalar_one_or_none.return_value = None
    session.execute.side_effect = [username_result, email_result, role_result]

    service = UserService(session)
    payload = UserCreate(
        username="tester",
        password="password123",
        nickname="Tester",
        email="test@example.com",
    )

    with pytest.raises(ValueError, match="Default user role not found"):
        await service.create_user(payload)
