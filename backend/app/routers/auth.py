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
            detail="아이디 또는 비밀번호가 올바르지 않습니다.",
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
        raise HTTPException(status_code=401, detail="유효하지 않거나 만료된 토큰입니다.")
    return TokenResponse(**new_token)


@router.post(
    "/change-password",
    summary="Change password",
    description="Change the current user's password.",
)
async def change_password(
    body: ChangePasswordRequest, current_user: CurrentUser, db: SessionDep
):
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
