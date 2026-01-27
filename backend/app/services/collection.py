import logging
from uuid import UUID, uuid4
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_, select, func
from sqlalchemy.orm import selectinload

from app.db import create_vectorstore_table, raw_sql
from app.models import Collection, User, EmbeddingSpec, ModelApiKey
from app.schemas import (
    CollectionCreate,
    CollectionUpdate,
    CollectionRead,
    PaginatedCollectionResponse,
)
from app.utils import is_admin_user as is_admin

from app.services.model_api_key import ModelApiKeyService

logger = logging.getLogger(__name__)


class CollectionService:
    def __init__(self, db: AsyncSession):
        """
        Why: 컬렉션 관련 작업에 사용할 DB 세션을 주입합니다.

        Args:
            db: 비동기 SQLAlchemy 세션.
        """
        self.db = db

    async def _resolve_embedding_spec(
        self, model: str, provider_id: int
    ) -> EmbeddingSpec | None:
        """
        Summary: 모델/프로바이더에 맞는 임베딩 사양을 조회합니다.

        Args:
            model: 임베딩 모델명.
            provider_id: 제공자 ID.

        Returns:
            EmbeddingSpec | None: 임베딩 사양 엔티티.

        Raises:
            HTTPException: 임베딩 사양이 없을 때.

        Side Effects:
            - DB 조회
        """
        res = await self.db.execute(
            select(EmbeddingSpec).where(
                EmbeddingSpec.model == model,
                EmbeddingSpec.provider_id == provider_id,
            )
        )
        emb_spec = res.scalar_one_or_none()

        if not emb_spec:
            raise HTTPException(
                status_code=404, detail="임베딩 사양을 찾을 수 없습니다."
            )
        return emb_spec

    async def _reslove_model_api_key(
        self,
        model_api_key_id: int,
        user: User,
    ) -> ModelApiKey | None:
        """
        Summary: 모델 API 키를 조회하고 접근 권한을 검증합니다.

        Args:
            model_api_key_id: 모델 API 키 ID.
            user: 요청 사용자.

        Returns:
            ModelApiKey | None: 키 엔티티.

        Raises:
            HTTPException: 키 미존재 또는 권한 없음.

        Side Effects:
            - DB 조회
        """
        model_api_key = await ModelApiKeyService(self.db).get(model_api_key_id)
        if not model_api_key:
            raise HTTPException(
                status_code=404, detail="Model API 키를 찾을 수 없습니다."
            )
        if not (
            model_api_key.is_active
            and (
                model_api_key.is_public
                or model_api_key.owner_id == user.id
                or is_admin(user)
            )
        ):
            raise HTTPException(
                status_code=403, detail="Model API 키에 접근할 수 없습니다."
            )

        return model_api_key

    async def get_orm_model(self, collection_id: UUID, user: User) -> Collection:
        """
        Summary: 권한 검증을 포함한 컬렉션 ORM 엔티티 조회.

        Args:
            collection_id: 컬렉션 ID.
            user: 요청 사용자.

        Returns:
            Collection: 컬렉션 엔티티.

        Raises:
            HTTPException: 컬렉션 미존재 또는 접근 권한 없음.

        Side Effects:
            - DB 조회
        """
        collection = await self.db.get(
            Collection, collection_id, options=(selectinload(Collection.embedding),)
        )
        if not collection:
            raise HTTPException(status_code=404, detail="컬렉션을 찾을 수 없습니다.")

        is_owner = user.id == collection.owner_id
        if not (collection.is_public or is_owner or is_admin(user)):
            raise HTTPException(status_code=403, detail="접근 권한이 없습니다.")

        return collection

    async def create(
        self,
        user: User,
        data: CollectionCreate,
    ) -> CollectionRead:
        """
        Summary: 컬렉션을 생성하고 벡터스토어 테이블을 준비합니다.

        Contract:
            - 컬렉션 임베딩 모델은 모델 API 키와 일치해야 합니다.

        Args:
            user: 요청 사용자.
            data: 컬렉션 생성 데이터.

        Returns:
            CollectionRead: 생성된 컬렉션 DTO.

        Raises:
            HTTPException: 임베딩/키 미존재, 생성 실패.

        Side Effects:
            - DB 컬렉션 레코드 생성
            - 벡터스토어 테이블 생성
        """
        api_key = await self._reslove_model_api_key(data.model_api_key_id, user=user)
        model_name = api_key.model
        provider_id = api_key.provider_id
        emb_spec = await self._resolve_embedding_spec(model_name, provider_id)

        collection = Collection(
            id=uuid4(),
            name=data.name,
            description=data.description,
            is_public=data.is_public,
            owner_id=user.id,
            embedding_id=emb_spec.id,
        )

        try:
            self.db.add(collection)
            await self.db.flush()
            collection.embedding = emb_spec
            await create_vectorstore_table(collection=collection)
            await self.db.commit()
            await self.db.refresh(collection)
        except Exception as e:
            await self.db.rollback()
            try:
                await raw_sql(
                    self.db,
                    f"DROP TABLE IF EXISTS {collection.table_name} CASCADE",
                )
            except Exception:
                pass
            error_id = uuid4().hex[:8]
            logger.exception(f"[{error_id}] 컬렉션 생성 중 오류 발생: {e!r}")
            raise HTTPException(
                status_code=500,
                detail=f"컬렉션 생성 중 오류 발생 (error_id={error_id})",
            ) from e

        return CollectionRead(
            collection_id=collection.id,
            table_id=collection.table_name,
            name=collection.name,
            embedding_id=collection.embedding_id,
            embedding_dimension=emb_spec.dimension,
            embedding_model=emb_spec.model,
            description=collection.description,
            is_public=collection.is_public,
            owner_id=collection.owner_id,
            document_count=0,
            chunk_count=0,
        )

    async def get(self, collection_id: UUID, user: User) -> CollectionRead:
        """
        Summary: 컬렉션 상세 정보와 문서/청크 카운트를 반환합니다.

        Args:
            collection_id: 컬렉션 ID.
            user: 요청 사용자.

        Returns:
            CollectionRead: 컬렉션 상세 DTO.

        Raises:
            HTTPException: 컬렉션 미존재 또는 접근 권한 없음.

        Side Effects:
            - DB 조회(raw SQL 포함)
        """
        collection = await self.db.get(
            Collection, collection_id, options=(selectinload(Collection.embedding),)
        )
        if not collection:
            raise HTTPException(status_code=404, detail="컬렉션을 찾을 수 없습니다.")

        is_owner = user.id == collection.owner_id
        if not (collection.is_public or is_owner or is_admin(user)):
            raise HTTPException(status_code=403, detail="접근 권한이 없습니다.")

        row = await raw_sql(
            self.db,
            f"""
            SELECT
                COUNT(DISTINCT file_id ) AS document_count,
                COUNT(*) AS chunk_count
            FROM {collection.table_name}
            """,
            one=True,
        )
        document_count = row.get("document_count", 0)
        chunk_count = row.get("chunk_count", 0)

        return CollectionRead(
            collection_id=collection.id,
            table_id=collection.table_name,
            name=collection.name,
            description=collection.description,
            is_public=collection.is_public,
            owner_id=collection.owner_id,
            document_count=document_count,
            chunk_count=chunk_count,
            embedding_id=collection.embedding_id,
            embedding_dimension=(
                collection.embedding.dimension if collection.embedding else None
            ),
            embedding_model=(
                collection.embedding.model if collection.embedding else None
            ),
        )

    async def get_list(
        self,
        user: User,
        limit: int = 20,
        offset: int = 0,
    ) -> PaginatedCollectionResponse:
        """
        Summary: 접근 가능한 컬렉션 목록을 페이지네이션으로 조회합니다.

        Contract:
            - 공개 컬렉션 또는 소유 컬렉션만 반환합니다.

        Args:
            user: 요청 사용자.
            limit: 페이지 크기.
            offset: 페이지 시작 위치.

        Returns:
            PaginatedCollectionResponse: 목록과 전체 개수.

        Side Effects:
            - DB 조회(raw SQL 포함)
        """
        is_admin_check = is_admin(user)
        condition = or_(
            Collection.is_public.is_(True),
            Collection.owner_id == user.id,
            is_admin_check,
        )

        total_count = await self.db.scalar(
            select(func.count()).select_from(Collection).where(condition)
        )

        result = await self.db.execute(
            select(Collection)
            .options(selectinload(Collection.embedding))
            .where(condition)
            .limit(limit)
            .offset(offset)
        )
        collections = result.scalars().all()

        items = []
        for row in collections:
            collection: Collection = row

            try:
                raw = await raw_sql(
                    self.db,
                    f"""
                    SELECT
                        COUNT(DISTINCT file_id) AS document_count,
                        COUNT(*) AS chunk_count
                    FROM {collection.table_name}
                    """,
                    one=True,
                )

                document_count = raw.get("document_count", 0)
                chunk_count = raw.get("chunk_count", 0)
            except Exception:
                document_count, chunk_count = 0, 0

            items.append(
                CollectionRead(
                    collection_id=collection.id,
                    table_id=collection.table_name,
                    name=collection.name,
                    description=collection.description,
                    is_public=collection.is_public,
                    owner_id=collection.owner_id,
                    document_count=document_count,
                    chunk_count=chunk_count,
                    embedding_id=collection.embedding_id,
                    embedding_dimension=(
                        collection.embedding.dimension if collection.embedding else None
                    ),
                    embedding_model=(
                        collection.embedding.model if collection.embedding else None
                    ),
                )
            )

        return PaginatedCollectionResponse(
            total_count=total_count,
            items=items,
        )

    async def update(
        self, collection_id: UUID, data: CollectionUpdate, user: User
    ) -> CollectionRead:
        """
        Summary: 컬렉션 메타데이터를 수정합니다.

        Args:
            collection_id: 컬렉션 ID.
            data: 변경 요청 데이터.
            user: 요청 사용자.

        Returns:
            CollectionRead: 수정된 컬렉션 DTO.

        Raises:
            HTTPException: 컬렉션 미존재 또는 권한 없음.

        Side Effects:
            - DB 컬렉션 레코드 업데이트
        """
        collection = await self.db.get(Collection, collection_id)
        if not collection:
            raise HTTPException(status_code=404, detail="컬렉션을 찾을 수 없습니다.")

        is_owner = user.id == collection.owner_id
        if not (is_owner or is_admin(user)):
            raise HTTPException(status_code=403, detail="수정 권한이 없습니다.")

        if data.name is not None:
            collection.name = data.name
        if data.description is not None:
            collection.description = data.description
        if data.is_public is not None:
            collection.is_public = data.is_public

        await self.db.commit()
        await self.db.refresh(collection)
        res = await self.db.execute(
            select(Collection)
            .options(selectinload(Collection.embedding))
            .where(Collection.id == collection_id)
        )
        collection = res.scalar_one()

        raw = await raw_sql(
            self.db,
            f"""
            SELECT
                COUNT(DISTINCT file_id) AS document_count,
                COUNT(*) AS chunk_count
            FROM {collection.table_name}
            """,
            one=True,
        )
        document_count = raw.get("document_count", 0)
        chunk_count = raw.get("chunk_count", 0)
        return CollectionRead(
            collection_id=collection.id,
            table_id=collection.table_name,
            name=collection.name,
            description=collection.description,
            is_public=collection.is_public,
            owner_id=collection.owner_id,
            document_count=document_count,
            chunk_count=chunk_count,
            embedding_id=collection.embedding_id,
            embedding_dimension=(
                collection.embedding.dimension if collection.embedding else None
            ),
            embedding_model=(
                collection.embedding.model if collection.embedding else None
            ),
        )

    async def delete(self, collection_id: UUID, user: User) -> None:
        """
        Summary: 컬렉션과 벡터 테이블을 삭제합니다.

        Args:
            collection_id: 컬렉션 ID.
            user: 요청 사용자.

        Raises:
            HTTPException: 컬렉션 미존재 또는 권한 없음.

        Side Effects:
            - 벡터 테이블 DROP
            - DB 컬렉션 레코드 삭제
        """
        collection = await self.db.get(Collection, collection_id)
        if not collection:
            raise HTTPException(status_code=404, detail="컬렉션을 찾을 수 없습니다.")

        is_owner = user.id == collection.owner_id
        if not (is_owner or is_admin(user)):
            raise HTTPException(status_code=403, detail="삭제 권한이 없습니다.")

        table_name = collection.table_name

        await raw_sql(
            self.db,
            f"DROP TABLE IF EXISTS {table_name} CASCADE",
        )

        await self.db.delete(collection)
        await self.db.commit()
