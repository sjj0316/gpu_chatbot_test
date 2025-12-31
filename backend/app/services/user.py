from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.user import User
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

        hashed_pw = hash_password(user_data.password)

        user = User(
            username=user_data.username,
            password=hashed_pw,
            nickname=user_data.nickname,
            email=user_data.email,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
