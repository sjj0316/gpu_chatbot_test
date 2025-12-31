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
    if not value:
        return None
    v = value.strip()
    if len(v) <= 8:
        return "*" * len(v)
    return f"{v[:4]}...{v[-4:]}"


def _ilike_pattern(term: str) -> str:
    t = (term or "").strip()
    t = t.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{t}%"


class ModelApiKeyService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _resolve_provider_id(self, code: str) -> int:
        code = code.lower()
        pid = await self.session.scalar(
            select(ModelProviderLkp.id).where(ModelProviderLkp.code == code)
        )
        if not pid:
            raise ValueError(f"존재하지 않는 provider_code: {code}")
        return pid

    async def _resolve_purpose_id(self, code: str) -> int:
        code = code.lower()
        puid = await self.session.scalar(
            select(ModelPurposeLkp.id).where(ModelPurposeLkp.code == code)
        )
        if not puid:
            raise ValueError(f"존재하지 않는 purpose_code: {code}")
        return puid

    async def create(self, owner_id: int, payload: ModelApiKeyCreate) -> ModelApiKey:
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

        obj = await self.session.get(
            ModelApiKey,
            obj.id,
            options=(
                undefer(ModelApiKey.api_key),
                selectinload(ModelApiKey.provider),
                selectinload(ModelApiKey.purpose),
                selectinload(ModelApiKey.owner),
            ),
        )

        return obj

    async def delete(self, obj: ModelApiKey) -> None:
        await self.session.delete(obj)
        await self.session.commit()

    @staticmethod
    def to_read(
        obj: ModelApiKey, *, reveal_secret: bool = False
    ) -> ModelApiKeyRead | ModelApiKeyReadWithSecret:
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
