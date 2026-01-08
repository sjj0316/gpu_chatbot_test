from fastapi import APIRouter, Depends, HTTPException, status
from app.dependencies import SessionDep, require_admin
from app.schemas import UserCreate, UserRead
from app.services import UserService

router = APIRouter(prefix="/users", tags=["User"])


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, db: SessionDep):
    service = UserService(db)
    try:
        created_user = await service.create_user(user)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
    return created_user


@router.get("", response_model=list[UserRead])
async def list_users(
    db: SessionDep,
    current_user = Depends(require_admin),
    limit: int = 50,
    offset: int = 0,
):
    _ = current_user
    service = UserService(db)
    return await service.list_users(limit=limit, offset=offset)
