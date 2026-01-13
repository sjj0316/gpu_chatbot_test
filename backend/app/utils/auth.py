from app.models import User


def is_admin_user(user: User) -> bool:
    """
    Why: 관리자 권한 여부를 빠르게 판별합니다.

    Args:
        user: 사용자 엔티티.

    Returns:
        bool: admin/system 역할 여부.
    """
    return user.role.code in ("admin", "system")


def is_system_user(user: User) -> bool:
    """
    Why: 시스템 계정 여부를 명시적으로 구분합니다.

    Args:
        user: 사용자 엔티티.

    Returns:
        bool: system 역할 여부.
    """
    return bool(getattr(user, "role", None)) and user.role.code == "system"
