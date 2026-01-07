from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, status, Path

from app.dependencies import SessionDep, CurrentUser
# ...existing code...
from app.schemas import (
    ModelApiKeyCreate,
    ModelApiKeyRead,
    ModelApiKeyReadWithSecret,
    ModelApiKeyUpdate,
)
from app.services import ModelApiKeyService
from app.utils import is_admin_user as is_admin

router = APIRouter(prefix="/api-keys", tags=["API Keys"])


@router.post(
    "",
    response_model=ModelApiKeyReadWithSecret,
    status_code=status.HTTP_201_CREATED,
    summary="API Key 등록",
    description="Model API Key를 등록합니다.",
)
async def create_model_key(
    payload: ModelApiKeyCreate,
    session: SessionDep,
    current_user: CurrentUser,
):
    svc = ModelApiKeyService(session)
    try:
        obj = await svc.create(owner_id=current_user.id, payload=payload)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
    return svc.to_read(obj, reveal_secret=True)


@router.get(
    "",
    response_model=list[ModelApiKeyRead],
    summary="API Key 목록",
    description="내 키와(옵션) 공개 키 목록을 조회합니다.",
)
async def list_model_keys(
    session: SessionDep,
    current_user: CurrentUser,
    include_public: bool = Query(True, description="내 키 + 공개 키 포함 여부"),
    provider_code: str | None = None,
    purpose_code: str | None = None,
    is_active: bool | None = None,
    limit: int = Query(10, ge=1, le=200),
    offset: int = Query(0, ge=0),
    owner_id: int | None = None,
):
    svc = ModelApiKeyService(session)

    if owner_id is not None and not is_admin(current_user):
        owner_id = current_user.id

    owner = current_user.id if owner_id is None else owner_id
    rows, _ = await svc.get_list(
        owner_id=owner,
        include_public=include_public,
        provider_code=provider_code,
        purpose_code=purpose_code,
        is_active=is_active,
        limit=limit,
        offset=offset,
    )
    return [svc.to_read(r) for r in rows]


@router.get(
    "/{key_id}",
    response_model=ModelApiKeyRead | ModelApiKeyReadWithSecret,
    summary="API Key 단건 조회",
)
async def get_model_key(
    session: SessionDep,
    current_user: CurrentUser,
    key_id: int = Path(ge=1),
    reveal_secret: bool = Query(False, description="소유자/관리자만 true 허용"),
) -> ModelApiKeyRead | ModelApiKeyReadWithSecret:
    svc = ModelApiKeyService(session)
    obj = await svc.get(key_id)
    if not obj:
        raise HTTPException(
            status_code=404, detail="Model API Key가 존재하지 않습니다."
        )

    can_view_secret = (obj.owner_id == current_user.id) or is_admin(current_user)
    if reveal_secret and not can_view_secret:
        raise HTTPException(status_code=403, detail="비밀키 열람 권한이 없습니다.")

    return svc.to_read(obj, reveal_secret=reveal_secret and can_view_secret)


@router.patch(
    "/{key_id}",
    response_model=ModelApiKeyReadWithSecret,
    summary="API Key 수정",
)
async def update_model_key(
    session: SessionDep,
    current_user: CurrentUser,
    key_id: int = Path(ge=1),
    payload: ModelApiKeyUpdate | None = None,
):
    svc = ModelApiKeyService(session)
    obj = await svc.get(key_id)
    if not obj:
        raise HTTPException(
            status_code=404, detail="Model API Key가 존재하지 않습니다."
        )
    if not (obj.owner_id == current_user.id or is_admin(current_user)):
        raise HTTPException(status_code=403, detail="수정 권한이 없습니다.")

    try:
        obj = await svc.update(obj, payload or ModelApiKeyUpdate())
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e

    return svc.to_read(obj, reveal_secret=True)


@router.delete(
    "/{key_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="API Key 삭제",
)
async def delete_model_key(
    session: SessionDep,
    current_user: CurrentUser,
    key_id: int = Path(ge=1),
):
    svc = ModelApiKeyService(session)
    obj = await svc.get(key_id)
    if not obj:
        raise HTTPException(
            status_code=404, detail="Model API Key가 존재하지 않습니다."
        )
    if not (obj.owner_id == current_user.id or is_admin(current_user)):
        raise HTTPException(status_code=403, detail="삭제 권한이 없습니다.")

    await svc.delete(obj)
    return None
