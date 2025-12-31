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

    def __init__(self, db: AsyncSession):
        self.db = db

    async def authenticate_user(self, login_data: LoginRequest) -> dict | None:
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
