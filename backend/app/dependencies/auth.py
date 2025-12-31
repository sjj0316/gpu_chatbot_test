from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.utils import decode_token
from app.models import User

from .session import get_db

api_key_header = APIKeyHeader(name="Authorization")


async def get_current_user(
    token: str = Depends(api_key_header), db: AsyncSession = Depends(get_db)
) -> User:
    token = token.removeprefix("Bearer ")

    payload = decode_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    username: str = payload["sub"]
    result = await db.execute(
        select(User).options(selectinload(User.role)).where(User.username == username)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    return user


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role.code not in ("admin", "system"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자만 가능합니다.",
        )
    return current_user


def verify_access_token(token: str = Depends(api_key_header)) -> dict:
    token = token.removeprefix("Bearer ")

    payload = decode_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    return payload
