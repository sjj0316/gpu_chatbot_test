from langchain_postgres import PGVectorStore, Column
from langchain_postgres.v2.hybrid_search_config import HybridSearchConfig
from asyncpg.exceptions import DuplicateTableError
from sqlalchemy import text

from .session import pg_engine, engine


async def _exec_many_ddl(stmts: list[str]) -> None:
    async with engine.begin() as conn:  # 트랜잭션 내 DDL (CONCURRENTLY 제외)
        for s in stmts:
            await conn.execute(text(s))


def _metric(collection) -> str:
    return (getattr(collection.embedding, "distance", None) or "cosine").lower()


def _opclass(dtype: str, metric: str) -> str:
    base = "halfvec" if dtype == "halfvec" else "vector"
    if metric in ("cosine", "cos"):
        return f"{base}_cosine_ops"
    if metric in ("l2", "euclidean"):
        return f"{base}_l2_ops"
    if metric in ("ip", "inner", "inner_product", "dot"):
        return f"{base}_ip_ops"
    return f"{base}_cosine_ops"


def get_metadata_columns() -> list[Column]:
    return [
        Column("file_id", "TEXT"),
        Column("chunk_index", "INTEGER"),
        Column("source", "TEXT"),
    ]


def _vec_ops_for(collection) -> str:
    metric = (getattr(collection.embedding, "distance", None) or "cosine").lower()
    if metric in ("cosine", "cos"):
        return "vector_cosine_ops"
    if metric in ("l2", "euclidean"):
        return "vector_l2_ops"
    if metric in ("ip", "inner", "inner_product", "dot"):
        return "vector_ip_ops"
    return "vector_cosine_ops"


def get_hybrid_config(collection_name: str) -> HybridSearchConfig:
    return HybridSearchConfig(
        tsv_column="content_tsv_simple",
        tsv_lang="simple",
        index_name=f"{collection_name}_tsv_simple_idx",
        index_type="GIN",
        primary_top_k=50,  # 벡터 상위 N
        secondary_top_k=50,  # FTS 상위 N
        # fusion_function은 RRF 등으로 바꿀 수 있음
    )


async def create_vectorstore_table(collection=None) -> None:
    table = collection.table_name
    dim = int(collection.embedding.dimension)
    metric = _metric(collection)
    try:
        await pg_engine.ainit_vectorstore_table(
            table_name=table,
            vector_size=dim,
            metadata_columns=get_metadata_columns(),
            hybrid_search_config=get_hybrid_config(table),
        )
    except DuplicateTableError:
        pass

    # 2) 공통 보강(DDL)
    common_stmts = [
        f"""
        ALTER TABLE {table}
        ADD COLUMN IF NOT EXISTS content_tsv_en tsvector
        GENERATED ALWAYS AS (to_tsvector('english', coalesce(content, ''))) STORED
        """,
        f"CREATE INDEX IF NOT EXISTS idx_{table}_tsv_en_gin ON {table} USING GIN (content_tsv_en)",
        f"CREATE INDEX IF NOT EXISTS idx_{table}_content_trgm ON {table} USING GIN (content gin_trgm_ops)",
        f"""
        ALTER TABLE {table}
        ALTER COLUMN langchain_metadata
        TYPE jsonb
        USING COALESCE((langchain_metadata)::jsonb, '{{}}'::jsonb)
        """,
        f"CREATE INDEX IF NOT EXISTS idx_{table}_metadata_gin ON {table} USING GIN (langchain_metadata)",
    ]
    await _exec_many_ddl(common_stmts)

    vec_ops = _opclass("vector", metric)

    if dim <= 2000:
        # HNSW + IVFFlat
        stmts = [
            f"CREATE INDEX IF NOT EXISTS idx_{table}_vec_hnsw ON {table} USING hnsw (embedding {vec_ops})",
            f"CREATE INDEX IF NOT EXISTS idx_{table}_vec_ivf  ON {table} USING ivfflat (embedding {vec_ops}) WITH (lists = 100)",
        ]
        await _exec_many_ddl(stmts)
    # else:
    #     # 2000 차원 초과: HNSW 금지, IVFFlat만 생성
    #     stmts = [
    #         f"CREATE INDEX IF NOT EXISTS idx_{table}_vec_ivf ON {table} USING ivfflat (embedding {vec_ops}) WITH (lists = 200)",
    #     ]
    #     await _exec_many_ddl(stmts)


async def get_vectorstore(
    collection, use_hybrid_search: bool = True, embedding=None
) -> PGVectorStore:
    collection_name = collection.table_name
    metadata_columns = get_metadata_columns()
    hybrid_config = get_hybrid_config(collection_name) if use_hybrid_search else None

    try:
        return await PGVectorStore.create(
            engine=pg_engine,
            table_name=collection_name,
            embedding_service=embedding,
            metadata_columns=[col.name for col in metadata_columns],
            hybrid_search_config=hybrid_config,
        )
    except Exception as e:
        raise RuntimeError(f"Vectorstore 초기화 실패 (인스턴스 생성): {e}")
