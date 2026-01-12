import json
import logging
import re
from typing import Any, Literal
from uuid import UUID, uuid4

from fastapi import HTTPException, UploadFile, status
from langchain_core.documents import Document
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_vectorstore, raw_sql
from app.models import Collection, ModelApiKey, User
from app.schemas import DocumentUploadResponse
from app.services.collection import CollectionService
from app.services.model_api_key import ModelApiKeyService
from app.utils import get_embedding, process_document
from app.utils import is_admin_user as is_admin

logger = logging.getLogger(__name__)

_ASCII_RE = re.compile(r"^[\x00-\x7F]+$")
_HANGUL_RE = re.compile(r"[\u3130-\u318F\uAC00-\uD7A3]")


def _choose_fts(detail: str) -> tuple[str, str]:
    if not detail or _HANGUL_RE.search(detail):
        return ("simple", "content_tsv_simple")
    if _ASCII_RE.match(detail):
        return ("english", "content_tsv_en")
    return ("simple", "content_tsv_simple")


class DocumentService:
    def __init__(self, db: AsyncSession, collection_id: UUID, user: User):
        self.db = db
        self.collection_id = collection_id
        self.user = user
        self.embedding = None

    async def _get_collection(self) -> Collection:
        """컬렉션 조회 후 없으면 raise"""
        collection = await CollectionService(self.db).get_orm_model(
            self.collection_id, self.user
        )
        return collection

    async def _reslove_model_api_key(self, model_api_key_id: int) -> ModelApiKey | None:
        model_api_key = await ModelApiKeyService(self.db).get(model_api_key_id)
        if not model_api_key:
            raise HTTPException(
                status_code=404, detail="Model API 키를 찾을 수 없습니다."
            )
        if not (
            model_api_key.is_active
            and (
                model_api_key.is_public
                or model_api_key.owner_id == str(self.user.id)
                or is_admin(self.user)
            )
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="해당 Model API 키에 접근할 권한이 없습니다.",
            )

        return model_api_key

    async def _auto_matched_api_key(self, collection: Collection) -> ModelApiKey | None:
        m = collection.embedding.model
        p = collection.embedding.provider_id
        model_api_key = await ModelApiKeyService(self.db).get_by_search(m, p)
        if not model_api_key:
            raise HTTPException(
                status_code=404, detail="Model API 키를 찾을 수 없습니다."
            )
        if not (
            model_api_key.is_active
            and (
                model_api_key.is_public
                or model_api_key.owner_id == str(self.user.id)
                or is_admin(self.user)
            )
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="해당 Model API 키에 접근할 권한이 없습니다.",
            )

        return model_api_key

    async def upsert(
        self, documents: list[Document], model_api_key: ModelApiKey
    ) -> list[str]:
        """컬렉션에 문서를 추가합니다"""
        collection = await self._get_collection()
        try:
            embed = get_embedding(
                model_name=collection.embedding.model, model_api_key=model_api_key
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        try:
            store = await get_vectorstore(
                collection=collection,
                embedding=embed,
            )
            added_ids = await store.aadd_documents(documents)
            return added_ids
        except HTTPException:
            raise
        except Exception as exc:
            error_id = uuid4().hex[:8]
            logger.exception(f"[{error_id}] 벡터스토어 추가 중 오류 발생: {exc!r}")
            raise HTTPException(
                status_code=500,
                detail=f"벡터스토어 추가 중 오류 발생 (error_id={error_id})",
            ) from exc

    async def create(
        self,
        files: list[UploadFile],
        metadatas: list[dict[str, Any] | None],
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        model_api_key_id: int = 1,
    ) -> DocumentUploadResponse:
        docs_to_index: list[Document] = []
        processed_files_count = 0
        failed_files: list[str] = []
        model_api_key = await self._reslove_model_api_key(model_api_key_id)
        collection = await self._get_collection()
        if (
            collection.embedding.model != model_api_key.model
            or model_api_key.provider_id != collection.embedding.provider_id
        ):
            raise HTTPException(
                status_code=400,
                detail="컬렉션의 임베딩 모델과 API 키의 모델이 일치하지 않습니다.",
            )

        for file, metadata in zip(files, metadatas, strict=False):
            try:
                docs = await process_document(
                    file=file,
                    metadata=metadata,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                )
                if docs:
                    docs_to_index.extend(docs)
                    processed_files_count += 1
                else:
                    logger.warning(f"파일에서 처리된 문서가 없습니다: {file.filename}")
            except Exception as e:
                logger.error(f"파일 처리 중 오류 발생: {file.filename} - {e}")
                failed_files.append(file.filename)

        if not docs_to_index:
            raise HTTPException(
                status_code=400,
                detail="업로드된 파일들로부터 처리 가능한 문서가 없습니다.",
            )

        added_ids = await self.upsert(docs_to_index, model_api_key=model_api_key)
        if not added_ids:
            error_id = uuid4().hex[:8]
            logger.error(f"[{error_id}] 벡터스토어에 문서를 추가하지 못했습니다.")
            raise HTTPException(
                status_code=500,
                detail=f"벡터스토어에 문서를 추가하지 못했습니다. (error_id={error_id})",
            )
        response = DocumentUploadResponse(
            success=True,
            message=f"{processed_files_count}개 파일에서 {len(added_ids)}개 청크를 추가했습니다.",
            added_chunk_ids=added_ids,
            warnings=(failed_files if failed_files else None),
        )
        return response

    async def get_list(
        self,
        *,
        limit: int = 10,
        offset: int = 0,
        view: Literal["chunk", "document"] = "document",
    ) -> dict:
        collection = await self._get_collection()
        table = collection.table_name
        count_row = await raw_sql(
            self.db,
            f"SELECT COUNT(*) AS chunk_count, COUNT(DISTINCT file_id) AS file_count FROM {table}",
            one=True,
        )

        chunk_total = count_row["chunk_count"]
        file_total = count_row["file_count"]
        if view == "document":
            rows = await raw_sql(
                self.db,
                f"""
                SELECT 
                    file_id,
                    source,
                    COUNT(*) AS chunk_count,
                    JSON_AGG(
                        JSON_BUILD_OBJECT(
                            'id', langchain_id,
                            'content', content,
                            'metadata', langchain_metadata,
                            'chunk_index', chunk_index
                        )
                        ORDER BY chunk_index
                    ) AS chunks
                FROM {table}
                GROUP BY file_id, source
                ORDER BY MAX(chunk_index)
                LIMIT :limit OFFSET :offset
                """,
                {"limit": limit, "offset": offset},
            )

            return {
                "items": [
                    {
                        "file_id": r["file_id"],
                        "source": r["source"],
                        "chunk_count": r["chunk_count"],
                        "chunks": [
                            {
                                "id": c["id"],
                                "content": c["content"],
                                "metadata": (
                                    c["metadata"]
                                    if isinstance(c["metadata"], dict)
                                    else (
                                        json.loads(c["metadata"])
                                        if c["metadata"]
                                        else {}
                                    )
                                ),
                                "chunk_index": c["chunk_index"],
                            }
                            for c in r["chunks"]
                        ],
                    }
                    for r in rows
                ],
                "chunk_total": chunk_total,
                "file_total": file_total,
            }

        rows = await raw_sql(
            self.db,
            f"""
            SELECT 
                langchain_id,
                content,
                file_id,
                chunk_index,
                source,
                langchain_metadata
            FROM {table}
            ORDER BY file_id, chunk_index
            LIMIT :limit OFFSET :offset
            """,
            {"limit": limit, "offset": offset},
        )

        docs = []
        for r in rows:
            metadata = {
                "file_id": r["file_id"],
                "chunk_index": r["chunk_index"],
                "source": r["source"],
            }
            if r["langchain_metadata"]:
                try:
                    metadata.update(json.loads(r["langchain_metadata"]))
                except Exception:
                    pass

            docs.append(
                {
                    "id": str(r["langchain_id"]),
                    "content": r["content"],
                    "metadata": metadata,
                    "source": r["source"],
                }
            )

        return {
            "items": docs,
            "chunk_total": chunk_total,
            "file_total": file_total,
        }

    async def delete_all(
        self,
        file_ids: list[UUID] | None = None,
        document_ids: list[UUID] | None = None,
    ) -> int:
        collection = await self._get_collection()

        if file_ids:
            result = await raw_sql(
                self.db,
                f"""
                DELETE FROM {collection.table_name}
                WHERE file_id = ANY(:file_ids)
                """,
                {"file_ids": [str(fid) for fid in file_ids]},
            )
        elif document_ids:
            result = await raw_sql(
                self.db,
                f"""
                DELETE FROM {collection.table_name}
                WHERE langchain_id = ANY(:document_ids)
                """,
                {"document_ids": [str(did) for did in document_ids]},
            )
        else:
            result = await raw_sql(
                self.db,
                f"DELETE FROM {collection.table_name}",
            )

        return result.rowcount

    async def delete_by(
        self,
        target_id: UUID,
        delete_by: Literal["document_id", "file_id"] = "file_id",
    ) -> int:
        collection = await self._get_collection()

        if delete_by == "document_id":
            query = f"""
                DELETE FROM {collection.table_name}
                WHERE langchain_id = :id
            """
        elif delete_by == "file_id":
            query = f"""
                DELETE FROM {collection.table_name}
                WHERE file_id = :id
            """
        else:
            raise ValueError("delete_by는 'file_id' 또는 'document_id'만 허용됩니다.")

        result = await raw_sql(
            self.db,
            query,
            {"id": str(target_id)},
        )
        return result.rowcount

    async def search(
        self,
        query: str,
        *,
        limit: int = 10,
        search_type: Literal["semantic", "keyword", "hybrid"] = "semantic",
        filter: dict[str, Any] | None = None,
        model_api_key_id: int = 1,
    ) -> list[dict[str, Any]]:
        if search_type not in {"semantic", "keyword", "hybrid"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid search type: {search_type}",
            )

        collection = await self._get_collection()
        model_api_key = await self._reslove_model_api_key(model_api_key_id)
        if (
            collection.embedding.model != model_api_key.model
            or model_api_key.provider_id != collection.embedding.provider_id
        ):
            model_api_key = await self._auto_matched_api_key(collection)

        try:
            embed = get_embedding(
                model_name=collection.embedding.model, model_api_key=model_api_key
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        table = collection.table_name

        if search_type == "keyword":
            cfg, col = _choose_fts(query)
            has_filter = bool(filter)
            if len(query.strip()) <= 2:
                rows = await raw_sql(
                    self.db,
                    f"""
                    SELECT langchain_id,
                        source,
                        content AS page_content,
                        langchain_metadata AS metadata
                    FROM {table}
                    WHERE content ILIKE ('%' || :q || '%')
                    {"  AND langchain_metadata @> CAST(:filter AS jsonb)" if has_filter else ""}
                    ORDER BY langchain_id DESC
                    LIMIT :limit
                    """,
                    {
                        "q": query,
                        "limit": limit,
                        "filter": json.dumps(filter) if filter else None,
                    },
                )
                return [
                    {
                        "id": str(r["langchain_id"]),
                        "page_content": r["page_content"],
                        "metadata": (
                            r["metadata"]
                            if isinstance(r["metadata"], dict)
                            else (json.loads(r["metadata"]) if r["metadata"] else {})
                        ),
                        "score": None,
                    }
                    for r in rows
                ]

            sql = f"""
            WITH q AS (SELECT websearch_to_tsquery(:cfg, :q) AS qs)
            SELECT
                langchain_id,
                source,
                content AS page_content,
                langchain_metadata AS metadata,
                ts_rank_cd({col}, q.qs) AS score
            FROM {table}, q
            WHERE {col} @@ q.qs
                {"  AND langchain_metadata @> CAST(:filter AS jsonb)" if has_filter else ""}
            ORDER BY score DESC
            LIMIT :limit
            """
            rows = await raw_sql(
                self.db,
                sql,
                {
                    "cfg": cfg,
                    "q": query,
                    "limit": limit,
                    "filter": json.dumps(filter) if filter else None,
                },
            )
            return [
                {
                    "id": str(r["langchain_id"]),
                    "page_content": r["page_content"],
                    "metadata": (
                        r["metadata"]
                        if isinstance(r["metadata"], dict)
                        else (json.loads(r["metadata"]) if r["metadata"] else {})
                    ),
                    "score": float(r["score"]) if r["score"] is not None else None,
                }
                for r in rows
            ]

        vf = filter or None
        k_candidates = max(limit, 100)

        try:
            # await raw_sql(self.db, "SET LOCAL ivfflat.probes = :p", {"p": 10})
            await raw_sql(
                self.db, "SET LOCAL hnsw.ef_search = :ef", {"ef": max(100, 2 * limit)}
            )
        except Exception:
            pass
        # semantic or hybrid → 벡터스토어 호출
        embed = get_embedding(
            model_name=collection.embedding.model, model_api_key=model_api_key
        )
        try:
            store = await get_vectorstore(
                collection=collection,
                use_hybrid_search=(search_type == "hybrid"),
                embedding=embed,
            )
            results = await store.asimilarity_search_with_score(
                query, k=k_candidates, filter=vf
            )
        except Exception as exc:
            error_id = uuid4().hex[:8]
            logger.exception(f"[{error_id}] 벡터스토어 검색 중 오류 발생: {exc!r}")
            raise HTTPException(
                status_code=500,
                detail=f"벡터스토어 검색 중 오류 발생 (error_id={error_id})",
            ) from exc
        results = results[:limit]
        return [
            {
                "id": doc.id,
                "page_content": doc.page_content,
                "metadata": doc.metadata,
                "score": score,
            }
            for doc, score in results
        ]
