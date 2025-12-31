from __future__ import annotations

import time
import jwt
from typing import Any, Optional

from app.core.config import settings


def issue_service_api_key(
    uid: int = 2,
    sub: str = "admin",
    role: str = "admin",
    scope: list[str] | None = None,
    issuer: str | None = None,
    audience: str | None = None,
) -> str:
    """
    만료(exp) 없이 HS256으로 서명한 장기 JWT를 발급한다.
    - uid=1: system 사용자
    - scope: ["rag.read", "rag.search"] 기본
    - iss/aud는 선택 (검증 로직을 두지 않는다면 생략 가능)
    """
    claims: dict[str, Any] = {
        "sub": sub,
        "uid": uid,
        "role": role,
        "iat": int(time.time()),
        "scope": scope or ["rag.read", "rag.search"],
    }
    if issuer:
        claims["iss"] = issuer
    if audience:
        claims["aud"] = audience

    return jwt.encode(
        claims,
        settings.jwt_secret_key,
        algorithm=settings.algorithm,  # "HS256"
    )
