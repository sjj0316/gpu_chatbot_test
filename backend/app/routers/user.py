from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.dependencies import CurrentUser, SessionDep, require_admin
from app.schemas import UserCreate, UserRead, UserUpdate
from app.services import UserService

router = APIRouter(prefix="/users", tags=["User"])


@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="사용자 등록",
    description="새 사용자 계정을 생성합니다.",
    responses={
        409: {"description": "중복 사용자/제약 조건 충돌"},
        422: {"description": "요청 본문 검증 실패"},
        500: {"description": "서버 오류"},
    },
)
async def register_user(user: UserCreate, db: SessionDep):
    """
    Why: 초기 계정 생성 흐름을 제공해 인증을 시작할 수 있게 합니다.

    Auth:
        - 필요 없음(공개 엔드포인트)

    Request/Response:
        - 요청: 사용자 생성 정보
        - 응답: 생성된 사용자 요약

    Errors:
        - 409: 중복 사용자 또는 제약 조건 충돌
        - 422: 요청 형식 오류

    Side Effects:
        - DB 사용자 레코드 생성
    """
    service = UserService(db)
    try:
        created_user = await service.create_user(user)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
    return created_user


@router.get(
    "",
    response_model=list[UserRead],
    summary="사용자 목록(관리자)",
    description="관리자 전용 사용자 목록 조회입니다.",
    responses={
        401: {"description": "인증 실패"},
        403: {"description": "관리자 권한 없음"},
        422: {"description": "쿼리 파라미터 검증 실패"},
        500: {"description": "서버 오류"},
    },
)
async def list_users(
    db: SessionDep,
    current_user=Depends(require_admin),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """
    Why: 운영자가 사용자 계정을 점검/관리할 수 있게 합니다.

    Auth:
        - 필요: 관리자 권한

    Request/Response:
        - 요청: limit/offset
        - 응답: 사용자 목록

    Errors:
        - 403: 관리자 권한이 없는 경우
        - 401/422: 인증 실패 또는 쿼리 형식 오류

    Side Effects:
        - 없음(조회 전용)
    """
    _ = current_user
    service = UserService(db)
    return await service.list_users(limit=limit, offset=offset)


@router.patch(
    "/me",
    response_model=UserRead,
    summary="내 정보 수정",
    description="현재 로그인 사용자 프로필을 업데이트합니다.",
    responses={
        401: {"description": "인증 실패"},
        409: {"description": "중복/제약 조건 충돌"},
        422: {"description": "요청 본문 검증 실패"},
        500: {"description": "서버 오류"},
    },
)
async def update_me(
    payload: UserUpdate, db: SessionDep, current_user: CurrentUser
):
    """
    Why: 사용자가 본인 프로필 정보를 수정할 수 있도록 합니다.

    Auth:
        - 필요: Bearer 토큰

    Request/Response:
        - 요청: 수정 가능한 사용자 필드
        - 응답: 수정된 사용자 정보

    Errors:
        - 409: 중복/제약 조건 충돌
        - 401/422: 인증 실패 또는 요청 형식 오류

    Side Effects:
        - DB 사용자 레코드 업데이트
    """
    service = UserService(db)
    try:
        updated_user = await service.update_profile(user=current_user, data=payload)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
    return updated_user
