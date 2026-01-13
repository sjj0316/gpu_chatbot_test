from typing import Dict

from fastapi import APIRouter, HTTPException, status

from app.dependencies import SessionDep, CurrentUser
from app.schemas import (
    UserRead,
    LoginRequest,
    TokenResponse,
    RefreshRequest,
    ChangePasswordRequest,
)
from app.services import AuthService, UserService


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get(
    "/me",
    response_model=UserRead,
    summary="내 정보 조회",
    description="인증 토큰으로 현재 로그인 사용자 정보를 조회합니다.",
    responses={
        401: {"description": "인증 실패(토큰 누락/만료/무효)"},
        500: {"description": "서버 오류"},
    },
)
async def get_my_info(current_user: CurrentUser):
    """
    Why: 현재 세션의 사용자 컨텍스트를 확인하기 위한 진입점입니다.

    Auth:
        - 필요: Bearer 토큰

    Request/Response:
        - 요청: 본문 없음
        - 응답: 사용자 프로필 요약(UserRead)

    Errors:
        - 401: 토큰이 없거나 만료/무효인 경우

    Side Effects:
        - 없음(조회 전용)
    """
    return current_user


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="로그인",
    description="아이디/비밀번호로 인증하고 액세스/리프레시 토큰을 발급합니다.",
    responses={
        401: {"description": "아이디 또는 비밀번호 불일치"},
        422: {"description": "요청 본문 검증 실패"},
        500: {"description": "서버 오류"},
    },
)
async def login(login_data: LoginRequest, db: SessionDep):
    """
    Why: 인증 성공 시 이후 API 호출에 필요한 토큰 쌍을 발급합니다.

    Auth:
        - 필요 없음(공개 엔드포인트)

    Request/Response:
        - 요청: username/password
        - 응답: access_token/refresh_token/token_type

    Errors:
        - 401: 자격 증명이 유효하지 않은 경우
        - 422: 요청 필드가 누락되거나 형식이 잘못된 경우

    Side Effects:
        - 토큰 발급(서버 측 세션/저장소 정책에 따라 기록될 수 있음)
    """
    service = AuthService(db)
    token = await service.authenticate_user(login_data)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="아이디 또는 비밀번호가 올바르지 않습니다.",
        )
    return token


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="토큰 재발급",
    description="유효한 refresh_token으로 access_token을 재발급합니다.",
    responses={
        401: {"description": "유효하지 않거나 만료된 refresh_token"},
        422: {"description": "요청 본문 검증 실패"},
        500: {"description": "서버 오류"},
    },
)
async def refresh_token(body: RefreshRequest, db: SessionDep):
    """
    Why: 액세스 토큰 만료 시 세션을 끊지 않고 재발급을 가능하게 합니다.

    Auth:
        - 필요 없음(리프레시 토큰으로 검증)

    Request/Response:
        - 요청: refresh_token
        - 응답: 신규 access_token/refresh_token/token_type

    Errors:
        - 401: refresh_token이 만료되었거나 서명 검증에 실패한 경우
        - 422: 요청 형식이 잘못된 경우

    Side Effects:
        - 토큰 재발급(서버 정책에 따라 기존 토큰 폐기 가능)
    """
    service = AuthService(db)
    new_token = await service.refresh_access_token(body.refresh_token)
    if not new_token:
        raise HTTPException(status_code=401, detail="유효하지 않거나 만료된 토큰입니다.")
    return TokenResponse(**new_token)


@router.post(
    "/change-password",
    summary="Change password",
    description="현재 로그인 사용자의 비밀번호를 변경합니다.",
    response_model=Dict[str, str],
    responses={
        400: {"description": "비밀번호 검증 실패(불일치/동일/현재 비밀번호 오류)"},
        401: {"description": "인증 실패(토큰 누락/만료/무효)"},
        422: {"description": "요청 본문 검증 실패"},
        500: {"description": "서버 오류"},
    },
)
async def change_password(
    body: ChangePasswordRequest, current_user: CurrentUser, db: SessionDep
):
    """
    Why: 사용자 계정 보안을 위해 스스로 비밀번호를 교체할 수 있게 합니다.

    Auth:
        - 필요: Bearer 토큰(본인 계정)

    Request/Response:
        - 요청: current_password/new_password/confirm_password
        - 응답: 처리 결과 메시지

    Errors:
        - 400: 새 비밀번호 불일치/현재 비밀번호 오류/새 비밀번호가 기존과 동일
        - 401: 인증 실패
        - 422: 요청 형식이 잘못된 경우

    Side Effects:
        - 사용자 비밀번호 변경(DB 업데이트)
    """
    if body.new_password != body.confirm_password:
        raise HTTPException(status_code=400, detail="새 비밀번호가 일치하지 않습니다.")
    if body.current_password == body.new_password:
        raise HTTPException(status_code=400, detail="새 비밀번호는 현재 비밀번호와 달라야 합니다.")

    service = UserService(db)
    try:
        await service.change_password(
            user_id=current_user.id,
            current_password=body.current_password,
            new_password=body.new_password,
        )
    except ValueError as exc:
        detail = str(exc)
        if detail == "Invalid current password":
            detail = "현재 비밀번호가 올바르지 않습니다."
        elif detail == "User not found":
            detail = "사용자를 찾을 수 없습니다."
        raise HTTPException(status_code=400, detail=detail) from exc

    return {"detail": "비밀번호가 변경되었습니다."}
