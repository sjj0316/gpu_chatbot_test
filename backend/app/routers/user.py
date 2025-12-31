from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.schemas import UserCreate, UserRead
from app.services import UserService

router = APIRouter(prefix="/users", tags=["User"])


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    service = UserService(db)
    created_user = await service.create_user(user)
    return created_user
