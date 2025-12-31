from typing import Any
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from langchain_postgres import PGEngine

from app.core import settings

engine = create_async_engine(
    settings.database_url,
    echo=True,
    pool_pre_ping=True,  # 죽은 커넥션 감지
    pool_recycle=1800,  # 장시간 유휴 방지
    # pool_size=5, max_overflow=10  # 필요시 명시
)
async_session = async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)
pg_engine = PGEngine.from_connection_string(url=settings.database_url)


class Base(DeclarativeBase):
    """SQL Alchemy Base Model"""

    pass


async def raw_sql(
    db: AsyncSession,
    query: str,
    params: dict[str, Any] | None = None,
    one: bool = False,
) -> Any:
    stmt = text(query)
    result = await db.execute(stmt, params or {})

    if result.returns_rows:
        result = result.mappings()  # <-- 컬럼 이름으로 접근 가능하게 변환
        return result.fetchone() if one else result.fetchall()
    else:
        await db.commit()
        return result
