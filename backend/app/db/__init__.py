from __future__ import annotations

from typing import Any, TYPE_CHECKING

from app.db.session import Base, async_session, engine, pg_engine, raw_sql

if TYPE_CHECKING:
    from app.db.vector import (  # pragma: no cover - typing only
        get_vectorstore as get_vectorstore_type,
        get_metadata_columns as get_metadata_columns_type,
        get_hybrid_config as get_hybrid_config_type,
        create_vectorstore_table as create_vectorstore_table_type,
    )


async def get_vectorstore(*args: Any, **kwargs: Any):
    # Lazy import to avoid heavy vector dependencies during module import.
    from app.db.vector import get_vectorstore as _get_vectorstore

    return await _get_vectorstore(*args, **kwargs)


def get_metadata_columns(*args: Any, **kwargs: Any):
    # Lazy import to avoid heavy vector dependencies during module import.
    from app.db.vector import get_metadata_columns as _get_metadata_columns

    return _get_metadata_columns(*args, **kwargs)


def get_hybrid_config(*args: Any, **kwargs: Any):
    # Lazy import to avoid heavy vector dependencies during module import.
    from app.db.vector import get_hybrid_config as _get_hybrid_config

    return _get_hybrid_config(*args, **kwargs)


async def create_vectorstore_table(*args: Any, **kwargs: Any):
    # Lazy import to avoid heavy vector dependencies during module import.
    from app.db.vector import create_vectorstore_table as _create_vectorstore_table

    return await _create_vectorstore_table(*args, **kwargs)

__all__ = [
    "Base",
    "engine",
    "pg_engine",
    "async_session",
    "get_vectorstore",
    "raw_sql",
    "get_metadata_columns",
    "get_hybrid_config",
    "create_vectorstore_table",
]
