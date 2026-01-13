from typing import Sequence

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, true, func
from sqlalchemy.orm import undefer, selectinload

from app.models import ModelApiKey, ModelProviderLkp, ModelPurposeLkp
from app.schemas import (
    ModelApiKeyCreate,
    ModelApiKeyRead,
    ModelApiKeyReadWithSecret,
    ModelApiKeyUpdate,
)


def _mask_key(value: str | None) -> str | None:
    """
    Why: 비밀키를 마스킹해 로그/응답에서 노출 위험을 줄입니다.

    Args:
        value: 원본 API 키 문자열.

    Returns:
        str | None: 앞/뒤 일부만 노출된 마스킹 문자열.
    """
    if not value:
        return None
    v = value.strip()
    if len(v) <= 8:
        return "*" * len(v)
    return f"{v[:4]}...{v[-4:]}"


def _ilike_pattern(term: str) -> str:
    """
    Why: ILIKE 검색을 위한 안전한 패턴을 생성합니다.

    Contract:
        - %, _ 특수문자를 이스케이프 처리합니다.

    Args:
        term: 검색어.

    Returns:
        str: ILIKE용 패턴 문자열.
    """
    t = (term or "").strip()
    t = t.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{t}%"


class ModelApiKeyService:
    """
    Summary: 모델 API 키의 생성/조회/갱신/삭제를 담당합니다.

    Contract:
        - provider/purpose 코드가 유효하지 않으면 ValueError를 발생시킵니다.
        - DB 제약 충돌은 ValueError로 변환합니다.

    Side Effects:
        - DB 레코드 생성/수정/삭제
    """
    def __init__(self, session: AsyncSession):
        """
        Why: 모델 API 키 작업에 사용할 DB 세션을 주입합니다.

        Args:
            session: 비동기 SQLAlchemy 세션.
        """
        self.session = session

    async def _resolve_provider_id(self, code: str) -> int:
        """
        Summary: provider_code를 FK ID로 변환합니다.

        Args:
            code: 제공자 코드.

        Returns:
            int: provider ID.

        Raises:
            ValueError: 제공자 코드가 존재하지 않는 경우.
        """
        code = code.lower()
        pid = await self.session.scalar(
            select(ModelProviderLkp.id).where(ModelProviderLkp.code == code)
        )
        if not pid:
            raise ValueError(f"존재하지 않는 provider_code: {code}")
        return pid

    async def _resolve_purpose_id(self, code: str) -> int:
        """
        Summary: purpose_code를 FK ID로 변환합니다.

        Args:
            code: 용도 코드.

        Returns:
            int: purpose ID.

        Raises:
            ValueError: 용도 코드가 존재하지 않는 경우.
        """
        code = code.lower()
        puid = await self.session.scalar(
            select(ModelPurposeLkp.id).where(ModelPurposeLkp.code == code)
        )
        if not puid:
            raise ValueError(f"존재하지 않는 purpose_code: {code}")
        return puid

    async def create(self, owner_id: int, payload: ModelApiKeyCreate) -> ModelApiKey:
        """
        Summary: 새로운 모델 API 키를 생성합니다.

        Contract:
            - provider_code/purpose_code는 사전에 등록되어 있어야 합니다.
            - 키 조합 중복 시 ValueError를 발생시킵니다.

        Args:
            owner_id: 키 소유자 사용자 ID.
            payload: 키 생성 요청 데이터.

        Returns:
            ModelApiKey: 생성된 키 엔티티.

        Raises:
            ValueError: 코드 불일치 또는 중복 제약 충돌.

        Side Effects:
            - DB 키 레코드 생성 및 커밋
        """
        pid = await self._resolve_provider_id(payload.provider_code)
        puid = await self._resolve_purpose_id(payload.purpose_code)

        obj = ModelApiKey(
            alias=payload.alias,
            provider_id=pid,
            model=payload.model,
            endpoint_url=payload.endpoint_url,
            purpose_id=puid,
            api_key=payload.api_key,
            is_public=payload.is_public,
            is_active=payload.is_active,
            extra=payload.extra,
            owner_id=owner_id,
        )
        self.session.add(obj)
        try:
            await self.session.flush()
        except IntegrityError as e:
            await self.session.rollback()
            raise ValueError(f"이미 존재하는 키 조합입니다: {e.orig}") from e

        await self.session.commit()
        await self.session.refresh(
            obj, attribute_names=["api_key", "provider", "purpose"]
        )
        return obj

    async def get_by_search(self, model: str, provider_id: int) -> ModelApiKey | None:
        """
        Summary: 모델명+provider로 키를 조회합니다.

        Args:
            model: 모델 식별자.
            provider_id: 제공자 ID.

        Returns:
            ModelApiKey | None: 키 엔티티 또는 None.

        Side Effects:
            - DB 조회
        """
        stmt = (
            select(ModelApiKey)
            .options(
                undefer(ModelApiKey.api_key),
                selectinload(ModelApiKey.owner),
                selectinload(ModelApiKey.provider),
                selectinload(ModelApiKey.purpose),
            )
            .where(
                and_(ModelApiKey.provider_id == provider_id, ModelApiKey.model == model)
            )
        )
        res = await self.session.execute(stmt)

        return res.scalar_one_or_none()

    async def get(self, key_id: int) -> ModelApiKey | None:
        """
        Summary: 키 ID로 단건 조회합니다.

        Args:
            key_id: 키 ID.

        Returns:
            ModelApiKey | None: 키 엔티티 또는 None.

        Side Effects:
            - DB 조회
        """
        stmt = (
            select(ModelApiKey)
            .options(
                undefer(ModelApiKey.api_key),
                selectinload(ModelApiKey.owner),
                selectinload(ModelApiKey.provider),
                selectinload(ModelApiKey.purpose),
            )
            .where(ModelApiKey.id == key_id)
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_list(
        self,
        *,
        owner_id: int | None = None,
        include_public: bool = False,
        provider_code: str | None = None,
        purpose_code: str | None = None,
        is_active: bool | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[Sequence[ModelApiKey], int]:
        """
        Summary: 조건에 맞는 키 목록과 전체 개수를 조회합니다.

        Contract:
            - include_public 여부에 따라 공개 키를 포함합니다.
            - provider_code/purpose_code는 부분 검색으로 처리합니다.

        Args:
            owner_id: 소유자 ID 필터.
            include_public: 공개 키 포함 여부.
            provider_code: 제공자 코드 검색어.
            purpose_code: 용도 코드 검색어.
            is_active: 활성 여부.
            limit: 페이지 크기.
            offset: 페이지 시작 위치.

        Returns:
            tuple[Sequence[ModelApiKey], int]: (키 목록, 총 개수).

        Side Effects:
            - DB 조회
        """
        conds = []
        if owner_id is not None and include_public:
            conds.append(
                or_(
                    ModelApiKey.owner_id == owner_id,
                    ModelApiKey.is_public.is_(True),
                )
            )
        elif owner_id is not None:
            conds.append(ModelApiKey.owner_id == owner_id)
        elif include_public:
            conds.append(ModelApiKey.is_public.is_(True))

        if provider_code:
            pattern = _ilike_pattern(provider_code)
            conds.append(
                ModelApiKey.provider.has(
                    ModelProviderLkp.code.ilike(pattern, escape="\\")
                )
            )

        if purpose_code:
            pattern = _ilike_pattern(purpose_code)
            conds.append(
                ModelApiKey.purpose.has(
                    ModelPurposeLkp.code.ilike(pattern, escape="\\")
                )
            )
        if is_active is not None:
            conds.append(ModelApiKey.is_active.is_(is_active))

        where = and_(*conds) if conds else true()

        total = (
            await self.session.execute(
                select(func.count()).select_from(ModelApiKey).where(where)
            )
        ).scalar_one()

        rows = (
            (
                await self.session.execute(
                    select(ModelApiKey)
                    .options(
                        undefer(ModelApiKey.api_key),
                        selectinload(ModelApiKey.owner),
                        selectinload(ModelApiKey.provider),
                        selectinload(ModelApiKey.purpose),
                    )
                    .where(where)
                    .order_by(ModelApiKey.id.desc())
                    .limit(limit)
                    .offset(offset)
                )
            )
            .scalars()
            .all()
        )

        return rows, total

    async def update(self, obj: ModelApiKey, payload: ModelApiKeyUpdate) -> ModelApiKey:
        """
        Summary: 키의 메타데이터/상태를 갱신합니다.

        Contract:
            - provider_code/purpose_code 변경 시 유효성 검사를 수행합니다.
            - 제약 충돌은 ValueError로 반환합니다.

        Args:
            obj: 수정 대상 키 엔티티.
            payload: 수정 요청 데이터.

        Returns:
            ModelApiKey: 갱신된 키 엔티티.

        Raises:
            ValueError: 제약 충돌 또는 코드 불일치.

        Side Effects:
            - DB 키 레코드 업데이트
        """
        simple_fields = (
            "alias",
            "model",
            "endpoint_url",
            "is_public",
            "is_active",
            "extra",
            "api_key",
        )
        for f in simple_fields:
            val = getattr(payload, f)
            if val is not None:
                setattr(obj, f, val)

        if payload.provider_code is not None:
            obj.provider_id = await self._resolve_provider_id(payload.provider_code)
        if payload.purpose_code is not None:
            obj.purpose_id = await self._resolve_purpose_id(payload.purpose_code)

        try:
            await self.session.flush()
        except IntegrityError as e:
            await self.session.rollback()
            raise ValueError(f"업데이트 충돌: {e.orig}") from e

        await self.session.commit()

        res = await self.session.execute(
            select(ModelApiKey)
            .options(
                undefer(ModelApiKey.api_key),
                selectinload(ModelApiKey.provider),
                selectinload(ModelApiKey.purpose),
                selectinload(ModelApiKey.owner),
            )
            .where(ModelApiKey.id == obj.id)
        )
        obj = res.scalar_one()

        return obj

    async def delete(self, obj: ModelApiKey) -> None:
        """
        Summary: 키를 삭제합니다.

        Args:
            obj: 삭제 대상 키 엔티티.

        Side Effects:
            - DB 키 레코드 삭제
        """
        await self.session.delete(obj)
        await self.session.commit()

    @staticmethod
    def to_read(
        obj: ModelApiKey, *, reveal_secret: bool = False
    ) -> ModelApiKeyRead | ModelApiKeyReadWithSecret:
        """
        Summary: DB 엔티티를 응답 스키마로 변환합니다.

        Contract:
            - reveal_secret이 True인 경우에만 원문 api_key를 포함합니다.

        Args:
            obj: 키 엔티티.
            reveal_secret: 비밀키 노출 여부.

        Returns:
            ModelApiKeyRead | ModelApiKeyReadWithSecret: 응답 스키마.
        """
        base = ModelApiKeyRead.model_validate(obj)
        base = base.model_copy(
            update={
                "provider_code": obj.provider.code if obj.provider else None,
                "purpose_code": obj.purpose.code if obj.purpose else None,
                "owner_nickname": obj.owner.nickname if obj.owner else None,
            }
        )
        base.api_key_masked = _mask_key(obj.api_key)

        if reveal_secret:
            data = base.model_dump()
            data["api_key"] = obj.api_key
            return ModelApiKeyReadWithSecret.model_validate(data)
        return base
