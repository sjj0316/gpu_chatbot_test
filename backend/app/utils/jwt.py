import jwt
from datetime import datetime, timedelta, timezone
from typing import Any

from app.core.config import settings

DEFAULT_TIMEZONE = timezone(timedelta(hours=9))


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Why: 액세스 토큰을 생성해 인증된 호출에 사용합니다.

    Contract:
        - exp 클레임을 반드시 포함합니다.

    Args:
        data: 토큰에 포함할 클레임.
        expires_delta: 만료 시간(옵션).

    Returns:
        str: 서명된 JWT 문자열.
    """
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
    """
    Why: 재발급용 리프레시 토큰을 생성합니다.

    Contract:
        - exp 클레임을 반드시 포함합니다.

    Args:
        data: 토큰에 포함할 클레임.
        expires_delta: 만료 시간(옵션).

    Returns:
        str: 서명된 JWT 문자열.
    """
    to_encode = data.copy()
    expire = datetime.now(DEFAULT_TIMEZONE) + (
        expires_delta or timedelta(minutes=settings.refresh_token_expire)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> dict[str, Any] | None:
    """
    Why: 토큰을 검증하고 클레임을 추출합니다.

    Contract:
        - 만료/서명 오류 시 None을 반환합니다.

    Args:
        token: JWT 문자열.

    Returns:
        dict[str, Any] | None: 디코딩된 클레임 또는 None.
    """
    try:
        return jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.algorithm]
        )
    except jwt.ExpiredSignatureError:
        return None
    except jwt.PyJWTError:
        return None
