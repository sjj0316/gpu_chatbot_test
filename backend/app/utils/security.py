from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Why: 평문 비밀번호를 안전한 해시로 변환합니다.

    Args:
        password: 평문 비밀번호.

    Returns:
        str: 해시된 비밀번호 문자열.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Why: 입력 비밀번호가 저장된 해시와 일치하는지 검증합니다.

    Args:
        plain_password: 입력한 평문 비밀번호.
        hashed_password: 저장된 해시 문자열.

    Returns:
        bool: 일치 여부.
    """
    return pwd_context.verify(plain_password, hashed_password)
