from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.user import User
from app.models.lookups import UserRoleLkp
from app.schemas.user import UserCreate
from app.utils.security import hash_password


class UserService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user_data: UserCreate) -> User:
        result = await self.db.execute(
            select(User).where(User.username == user_data.username)
        )
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise ValueError("Username already exists")

        result = await self.db.execute(select(User).where(User.email == user_data.email))
        existing_email = result.scalar_one_or_none()
        if existing_email:
            raise ValueError("Email already exists")

        result = await self.db.execute(
            select(UserRoleLkp.id).where(UserRoleLkp.code == "user")
        )
        role_id = result.scalar_one_or_none()
        if not role_id:
            raise ValueError("Default user role not found")

        hashed_pw = hash_password(user_data.password)

        user = User(
            username=user_data.username,
            password=hashed_pw,
            nickname=user_data.nickname,
            email=user_data.email,
            role_id=role_id,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def list_users(self, *, limit: int = 50, offset: int = 0) -> list[User]:
        result = await self.db.execute(
            select(User).order_by(User.id.desc()).limit(limit).offset(offset)
        )
        return result.scalars().all()
