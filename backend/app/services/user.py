from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.user import User
from app.models.lookups import UserRoleLkp
from app.schemas.user import UserCreate, UserUpdate
from app.utils.security import hash_password, verify_password


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

    async def update_profile(self, *, user: User, data: UserUpdate) -> User:
        if data.email and data.email != user.email:
            result = await self.db.execute(
                select(User).where(User.email == data.email, User.id != user.id)
            )
            existing_email = result.scalar_one_or_none()
            if existing_email:
                raise ValueError("Email already exists")
            user.email = data.email

        if data.nickname is not None:
            user.nickname = data.nickname

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def change_password(
        self, *, user_id: int, current_password: str, new_password: str
    ) -> None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError("User not found")

        if not verify_password(current_password, user.password):
            raise ValueError("Invalid current password")

        user.password = hash_password(new_password)
        self.db.add(user)
        await self.db.commit()
