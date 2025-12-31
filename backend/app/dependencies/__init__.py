from app.dependencies.auth import get_current_user, require_admin, verify_access_token
from app.dependencies.session import get_db

# alias
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.models import User

SessionDep = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
##

__all__ = [
    "get_current_user",
    "get_db",
    "require_admin",
    "verify_access_token",
    "SessionDep",
    "CurrentUser",
]
