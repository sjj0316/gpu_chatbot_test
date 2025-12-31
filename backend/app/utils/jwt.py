import jwt
from datetime import datetime, timedelta, timezone
from typing import Any

from app.core.config import settings

DEFAULT_TIMEZONE = timezone(timedelta(hours=9))


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(DEFAULT_TIMEZONE) + (
        expires_delta or timedelta(minutes=settings.access_token_expire)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.algorithm,
    )
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(DEFAULT_TIMEZONE) + (
        expires_delta or timedelta(minutes=settings.refresh_token_expire)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> dict[str, Any] | None:
    try:
        return jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.algorithm]
        )
    except jwt.ExpiredSignatureError:
        return None
    except jwt.PyJWTError:
        return None
