from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.schemas import CollectionCreate
from app.services.collection import CollectionService


@pytest.mark.asyncio
async def test_collection_create_rolls_back_on_vectorstore_failure(monkeypatch):
    session = MagicMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.rollback = AsyncMock()

    svc = CollectionService(session)
    monkeypatch.setattr(
        svc, "_reslove_model_api_key", AsyncMock(return_value=SimpleNamespace(model="m", provider_id=1))
    )
    monkeypatch.setattr(
        svc, "_resolve_embedding_spec", AsyncMock(return_value=SimpleNamespace(id=1, model="m", dimension=1536))
    )
    drop_calls = []

    async def fake_raw_sql(db, sql, *args, **kwargs):
        drop_calls.append(sql)
        return SimpleNamespace(rowcount=0)

    monkeypatch.setattr("app.services.collection.raw_sql", fake_raw_sql)
    monkeypatch.setattr(
        "app.services.collection.create_vectorstore_table",
        AsyncMock(side_effect=RuntimeError("fail")),
    )

    with pytest.raises(HTTPException):
        await svc.create(
            user=SimpleNamespace(id=1),
            data=CollectionCreate(name="c1", description=None, is_public=False),
        )

    session.rollback.assert_awaited_once()
    session.commit.assert_not_awaited()
    assert any("DROP TABLE IF EXISTS" in call for call in drop_calls)
