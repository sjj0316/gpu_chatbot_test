from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.schemas import MCPServerUpdate, MCPServerRuntime
from app.services.mcp_server import MCPServerService


class FakeRole:
    def __init__(self, code: str) -> None:
        # 인가 테스트용 최소 Role 객체.
        self.code = code


class FakeUser:
    def __init__(self, user_id: int, role_code: str = "user") -> None:
        # 소유/관리자 체크용 최소 User 객체.
        self.id = user_id
        self.role = FakeRole(role_code)


def _make_server(owner_id: int, is_public: bool = False) -> SimpleNamespace:
    # 서비스 테스트용 가짜 MCP 서버 모델 생성.
    return SimpleNamespace(
        id=1,
        name="Demo MCP",
        description="test",
        config={"transport": "http", "url": "http://localhost:9000"},
        is_public=is_public,
        owner_id=owner_id,
    )


class _Result:
    def __init__(self, obj=None):
        self._obj = obj

    def scalar_one_or_none(self):
        return self._obj


@pytest.mark.asyncio
async def test_get_mcp_server_denied_for_private_non_owner(monkeypatch: pytest.MonkeyPatch):
    # 준비: 다른 소유자의 비공개 서버.
    session = MagicMock()
    session.execute = AsyncMock(
        return_value=_Result(_make_server(owner_id=2, is_public=False))
    )

    # 실행/검증: 비소유자 403 차단.
    service = MCPServerService(session)
    with pytest.raises(HTTPException) as exc:
        await service.get(1, user=FakeUser(1, "user"))

    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_get_mcp_server_allows_public(monkeypatch: pytest.MonkeyPatch):
    # 준비: 공개 서버와 런타임 프로브 모킹.
    session = MagicMock()
    session.execute = AsyncMock(
        return_value=_Result(_make_server(owner_id=2, is_public=True))
    )
    monkeypatch.setattr(
        "app.services.mcp_server.probe_mcp_server",
        AsyncMock(return_value=MCPServerRuntime(reachable=True, tools=[])),
    )

    # 실행: 비소유자도 공개 서버 조회 가능.
    service = MCPServerService(session)
    dto = await service.get(1, user=FakeUser(1, "user"))

    # 검증: 반환 DTO에 공개 서버 데이터 반영.
    assert dto.id == 1
    assert dto.is_public is True


@pytest.mark.asyncio
async def test_update_mcp_server_denied_for_non_owner():
    # 준비: 다른 소유자의 비공개 서버.
    session = MagicMock()
    session.execute = AsyncMock(
        return_value=_Result(_make_server(owner_id=2, is_public=False))
    )

    # 실행/검증: 비소유자 업데이트 403.
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
    # 준비: 관리자가 비공개 서버 업데이트.
    session = MagicMock()
    server = _make_server(owner_id=2, is_public=False)
    session.execute = AsyncMock(return_value=_Result(server))
    session.scalar = AsyncMock(return_value=None)
    session.commit = AsyncMock()
    session.refresh = AsyncMock()

    # 실행: 관리자 권한으로 업데이트.
    service = MCPServerService(session)
    dto = await service.update(
        1,
        MCPServerUpdate(name="Updated", is_public=True),
        user=FakeUser(1, "admin"),
    )

    # 검증: 업데이트 적용 및 커밋.
    assert dto.name == "Updated"
    assert server.is_public is True
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_mcp_server_denied_for_non_owner():
    # 준비: 다른 소유자의 비공개 서버.
    session = MagicMock()
    session.execute = AsyncMock(
        return_value=_Result(_make_server(owner_id=2, is_public=False))
    )

    # 실행/검증: 비소유자 삭제 403.
    service = MCPServerService(session)
    with pytest.raises(HTTPException) as exc:
        await service.delete(1, user=FakeUser(1, "user"))

    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_get_masks_sensitive_config(monkeypatch: pytest.MonkeyPatch):
    # 준비: 민감정보가 포함된 config를 가진 서버.
    session = MagicMock()
    session.execute = AsyncMock(
        return_value=_Result(_make_server(owner_id=1, is_public=True))
    )
    server = session.execute.return_value.scalar_one_or_none()
    server.config = {
        "transport": "http",
        "url": "http://localhost:9000",
        "api_key": "secret",
        "headers": {"Authorization": "Bearer token"},
    }
    monkeypatch.setattr(
        "app.services.mcp_server.probe_mcp_server",
        AsyncMock(return_value=MCPServerRuntime(reachable=True, tools=[])),
    )

    service = MCPServerService(session)
    dto = await service.get(1, user=FakeUser(1, "user"))

    assert dto.config["api_key"] == "***"
    assert dto.config["headers"]["Authorization"] == "***"
