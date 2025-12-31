from fastapi import APIRouter, HTTPException, status

from app.dependencies import SessionDep, CurrentUser
from app.schemas import (
    UserRead,
    LoginRequest,
    TokenResponse,
    RefreshRequest,
)
from app.services import AuthService


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get(
    "/me",
    response_model=UserRead,
    summary="내 정보 조회",
    description="현재 로그인한 유저의 정보를 확인합니다.",
)
async def get_my_info(current_user: CurrentUser):
    return current_user


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="로그인",
    description="사용자의 아이디와 비밀번호로 로그인합니다.",
)
async def login(login_data: LoginRequest, db: SessionDep):
    service = AuthService(db)
    token = await service.authenticate_user(login_data)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    return token


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="토큰 재발급",
    description="refresh_token을 통해 access_token을 재발급 받습니다.",
)
async def refresh_token(body: RefreshRequest, db: SessionDep):
    service = AuthService(db)
    new_token = await service.refresh_access_token(body.refresh_token)
    if not new_token:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    return TokenResponse(**new_token)
