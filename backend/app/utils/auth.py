from app.models import User


def is_admin_user(user: User) -> bool:
    return user.role.code in ("admin", "system")


def is_system_user(user: User) -> bool:
    return bool(getattr(user, "role", None)) and user.role.code == "system"
