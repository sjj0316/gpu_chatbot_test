from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import User
from app.schemas import LoginRequest
from app.utils import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)


class AuthService:
    """
    Summary: 사용자 인증/토큰 발급 흐름을 캡슐화합니다.

    Contract:
        - 입력은 LoginRequest 또는 refresh_token 문자열입니다.
        - 성공 시 access_token/refresh_token을 반환하고 실패 시 None을 반환합니다.

    Side Effects:
        - DB 조회
        - JWT 생성
    """

    def __init__(self, db: AsyncSession):
        """
        Why: 인증 관련 DB 조회를 수행할 세션을 주입합니다.

        Args:
            db: 비동기 SQLAlchemy 세션.
        """
        self.db = db

    async def authenticate_user(self, login_data: LoginRequest) -> dict | None:
        """
        Summary: 사용자 자격 증명을 검증하고 토큰을 발급합니다.

        Contract:
            - username/password가 모두 일치해야 토큰을 반환합니다.
            - 실패 시 None을 반환하며 예외를 발생시키지 않습니다.

        Args:
            login_data: 로그인 요청 정보.

        Returns:
            dict | None: access_token/refresh_token 또는 None.

        Side Effects:
            - DB 조회
            - JWT 생성
        """
        result = await self.db.execute(
            select(User).where(User.username == login_data.username)
        )
        user = result.scalar_one_or_none()

        if not user:
            return None

        if not verify_password(login_data.password, user.password):
            return None

        access_token = create_access_token(data={"sub": user.username})
        refresh_token = create_refresh_token(data={"sub": user.username})

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    async def refresh_access_token(self, refresh_token: str) -> dict | None:
        """
        Summary: refresh_token을 검증하고 새 토큰 쌍을 발급합니다.

        Contract:
            - 토큰이 유효하고 사용자 존재 시에만 새 토큰을 반환합니다.
            - 실패 시 None을 반환합니다.

        Args:
            refresh_token: 리프레시 토큰 문자열.

        Returns:
            dict | None: 신규 access_token/refresh_token 또는 None.

        Side Effects:
            - DB 조회
            - JWT 생성
        """
        payload = decode_token(refresh_token)
        if not payload or "sub" not in payload:
            return None

        username = payload["sub"]
        result = await self.db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()
        if not user:
            return None

        new_access_token = create_access_token({"sub": username})
        new_refresh_token = create_refresh_token({"sub": username})

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
        }
