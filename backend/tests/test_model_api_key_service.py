from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from app.schemas import ModelApiKeyCreate
from app.services.model_api_key import ModelApiKeyService


@pytest.mark.asyncio
async def test_create_model_api_key_duplicate_raises_value_error():
    session = MagicMock()
    session.add = MagicMock()
    session.flush = AsyncMock(
        side_effect=IntegrityError("dup", params=None, orig=Exception("dup"))
    )
    session.rollback = AsyncMock()

    svc = ModelApiKeyService(session)
    svc._resolve_provider_id = AsyncMock(return_value=1)
    svc._resolve_purpose_id = AsyncMock(return_value=2)

    payload = ModelApiKeyCreate(
        alias="a",
        provider_code="openai",
        model="gpt-4o",
        endpoint_url=None,
        purpose_code="chat",
        api_key="secret",
        is_public=False,
        is_active=True,
        extra=None,
    )

    with pytest.raises(ValueError):
        await svc.create(owner_id=1, payload=payload)

    session.rollback.assert_awaited_once()
