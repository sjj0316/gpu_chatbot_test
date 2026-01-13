from __future__ import annotations

from fastapi import APIRouter, HTTPException, Path, Query, status

from app.dependencies import CurrentUser, SessionDep
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
    description="현재 사용자 소유의 모델 API 키를 등록합니다.",
    responses={
        401: {"description": "인증 실패"},
        409: {"description": "중복 키/제약 조건 충돌"},
        422: {"description": "요청 본문 검증 실패"},
        500: {"description": "서버 오류"},
    },
)
async def create_model_key(
    payload: ModelApiKeyCreate,
    session: SessionDep,
    current_user: CurrentUser,
):
    """
    Why: 외부 모델 제공자의 API 키를 서버에 안전하게 등록해 재사용합니다.

    Auth:
        - 필요: Bearer 토큰

    Request/Response:
        - 요청: provider/purpose/secret/metadata 등 등록 정보
        - 응답: 등록된 키 요약 + 비밀키(등록 직후 1회 노출)

    Errors:
        - 409: 동일 키/식별자 충돌 또는 제약 위반
        - 401/422: 인증 실패 또는 요청 형식 오류

    Side Effects:
        - DB에 키 레코드 생성
    """
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
    description="내 키와(옵션) 공개 키 목록을 필터/페이지네이션으로 조회합니다.",
    responses={
        401: {"description": "인증 실패"},
        403: {"description": "권한 없는 owner_id 조회 시도"},
        422: {"description": "쿼리 파라미터 검증 실패"},
        500: {"description": "서버 오류"},
    },
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
    """
    Why: 사용자 또는 관리자 관점에서 등록된 모델 API 키를 탐색/관리합니다.

    Auth:
        - 필요: Bearer 토큰

    Request/Response:
        - 요청: include_public/provider_code/purpose_code/is_active/limit/offset
        - 응답: 키 요약 목록(비밀값 제외)
        - 페이징: limit/offset 기반

    Errors:
        - 403: 관리자 권한 없이 owner_id를 타 사용자로 지정한 경우
        - 401/422: 인증 실패 또는 쿼리 형식 오류

    Side Effects:
        - 없음(조회 전용)
    """
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
    description="키 상세를 조회하며 비밀키는 소유자/관리자만 열람 가능합니다.",
    responses={
        401: {"description": "인증 실패"},
        403: {"description": "비밀키 열람 권한 없음"},
        404: {"description": "키가 존재하지 않음"},
        422: {"description": "경로/쿼리 파라미터 검증 실패"},
        500: {"description": "서버 오류"},
    },
)
async def get_model_key(
    session: SessionDep,
    current_user: CurrentUser,
    key_id: int = Path(ge=1),
    reveal_secret: bool = Query(False, description="소유자/관리자만 true 허용"),
) -> ModelApiKeyRead | ModelApiKeyReadWithSecret:
    """
    Why: 운영/디버깅 시 특정 키의 상태와 속성을 확인합니다.

    Auth:
        - 필요: Bearer 토큰

    Request/Response:
        - 요청: key_id, reveal_secret(옵션)
        - 응답: 키 상세(비밀값은 권한자만)

    Errors:
        - 404: 키가 존재하지 않는 경우
        - 403: 비밀키 공개 요청 권한 없음
        - 401/422: 인증 실패 또는 파라미터 오류

    Side Effects:
        - 없음(조회 전용)
    """
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
    description="키의 메타데이터/활성 상태 등을 수정합니다.",
    responses={
        401: {"description": "인증 실패"},
        403: {"description": "수정 권한 없음"},
        404: {"description": "키가 존재하지 않음"},
        409: {"description": "제약 조건 충돌"},
        422: {"description": "요청 본문/경로 검증 실패"},
        500: {"description": "서버 오류"},
    },
)
async def update_model_key(
    session: SessionDep,
    current_user: CurrentUser,
    key_id: int = Path(ge=1),
    payload: ModelApiKeyUpdate | None = None,
):
    """
    Why: 키 상태/메타데이터 변경으로 운영 정책을 조정합니다.

    Auth:
        - 필요: Bearer 토큰(소유자/관리자)

    Request/Response:
        - 요청: 수정 가능한 필드 일부 또는 빈 객체
        - 응답: 수정된 키(비밀값 포함)

    Errors:
        - 403: 소유자/관리자가 아닌 경우
        - 404: 키가 존재하지 않는 경우
        - 409: 중복/제약 조건 충돌
        - 401/422: 인증 실패 또는 요청 형식 오류

    Side Effects:
        - DB 키 레코드 업데이트
    """
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
    description="키를 영구 삭제합니다.",
    responses={
        401: {"description": "인증 실패"},
        403: {"description": "삭제 권한 없음"},
        404: {"description": "키가 존재하지 않음"},
        422: {"description": "경로 파라미터 검증 실패"},
        500: {"description": "서버 오류"},
    },
)
async def delete_model_key(
    session: SessionDep,
    current_user: CurrentUser,
    key_id: int = Path(ge=1),
):
    """
    Why: 더 이상 사용하지 않는 키를 안전하게 제거합니다.

    Auth:
        - 필요: Bearer 토큰(소유자/관리자)

    Request/Response:
        - 요청: key_id
        - 응답: 없음(204)

    Errors:
        - 403: 소유자/관리자가 아닌 경우
        - 404: 키가 존재하지 않는 경우
        - 401/422: 인증 실패 또는 경로 파라미터 오류

    Side Effects:
        - DB 키 레코드 삭제
    """
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
