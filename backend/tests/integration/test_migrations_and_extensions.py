from __future__ import annotations

from pathlib import Path
import subprocess

import pytest
import asyncpg

from .conftest import database_url


@pytest.mark.asyncio
async def test_migrations_and_extensions():
    # alembic 마이그레이션을 최신 상태로 올린다.
    backend_root = Path(__file__).resolve().parents[2]
    subprocess.run(
        ["uv", "run", "alembic", "upgrade", "head"],
        check=True,
        cwd=str(backend_root),
    )

    # 확장 및 테이블 생성 여부를 DB에서 직접 확인한다.
    conn = await asyncpg.connect(database_url())
    try:
        ext_rows = await conn.fetch(
            "SELECT extname FROM pg_extension WHERE extname IN ('pg_trgm', 'vector')"
        )
        ext_names = {row["extname"] for row in ext_rows}
        assert ext_names == {"pg_trgm", "vector"}

        version = await conn.fetchval("SELECT to_regclass('public.alembic_version')")
        assert version == "alembic_version"

        wiki_table = await conn.fetchval("SELECT to_regclass('public.wiki_pages')")
        assert wiki_table == "wiki_pages"
    finally:
        await conn.close()
