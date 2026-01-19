from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.schemas.user import UserCreate
from app.services.user import UserService


@pytest.mark.asyncio
async def test_create_user_success(monkeypatch: pytest.MonkeyPatch):
    # 준비: 비동기 DB 호출/사이드이펙트를 가진 가짜 세션 준비.
    session = MagicMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.add = MagicMock()

    # 준비: 사용자명/이메일 중복 및 역할 조회 결과 시뮬레이션.
    username_result = MagicMock()
    username_result.scalar_one_or_none.return_value = None
    email_result = MagicMock()
    email_result.scalar_one_or_none.return_value = None
    role_result = MagicMock()
    role_result.scalar_one_or_none.return_value = 2
    session.execute.side_effect = [username_result, email_result, role_result]

    # 준비: 실제 해싱 대신 고정 해시 반환.
    monkeypatch.setattr("app.services.user.hash_password", lambda pw: "hashed")

    # 실행: 유효한 사용자 페이로드로 서비스 호출.
    service = UserService(session)
    payload = UserCreate(
        username="tester",
        password="password123",
        nickname="Tester",
        email="test@example.com",
    )
    user = await service.create_user(payload)

    # 검증: ORM 모델이 추가/저장되고 기대 필드로 반환.
    session.add.assert_called_once()
    added_user = session.add.call_args[0][0]
    assert user == added_user
    assert added_user.role_id == 2
    assert added_user.password == "hashed"
    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once_with(added_user)


@pytest.mark.asyncio
async def test_create_user_duplicate_username():
    # 준비: 사용자명 중복 체크에 기존 행 반환.
    session = MagicMock()
    session.execute = AsyncMock()

    username_result = MagicMock()
    username_result.scalar_one_or_none.return_value = SimpleNamespace()
    session.execute.return_value = username_result

    # 실행/검증: 사용자 생성 시 사용자명 중복 오류.
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
    # 준비: 사용자명 통과, 이메일 중복 행 반환.
    session = MagicMock()
    session.execute = AsyncMock()

    username_result = MagicMock()
    username_result.scalar_one_or_none.return_value = None
    email_result = MagicMock()
    email_result.scalar_one_or_none.return_value = SimpleNamespace()
    session.execute.side_effect = [username_result, email_result]

    # 실행/검증: 사용자 생성 시 이메일 중복 오류.
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
    # 준비: 사용자명/이메일 통과, 기본 역할 없음.
    session = MagicMock()
    session.execute = AsyncMock()

    username_result = MagicMock()
    username_result.scalar_one_or_none.return_value = None
    email_result = MagicMock()
    email_result.scalar_one_or_none.return_value = None
    role_result = MagicMock()
    role_result.scalar_one_or_none.return_value = None
    session.execute.side_effect = [username_result, email_result, role_result]

    # 실행/검증: 기본 역할 조회 None이면 생성 실패.
    service = UserService(session)
    payload = UserCreate(
        username="tester",
        password="password123",
        nickname="Tester",
        email="test@example.com",
    )

    with pytest.raises(ValueError, match="Default user role not found"):
        await service.create_user(payload)
