from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.user import User
from app.models.lookups import UserRoleLkp
from app.schemas.user import UserCreate, UserUpdate
from app.utils.security import hash_password, verify_password


class UserService:
    """
    Summary: 사용자 계정 생성/조회/수정 로직을 담당합니다.

    Contract:
        - 중복 계정/이메일은 ValueError로 처리합니다.
        - DB 트랜잭션 커밋 및 리프레시를 수행합니다.

    Side Effects:
        - DB 레코드 생성/수정
    """

    def __init__(self, db: AsyncSession):
        """
        Why: 사용자 관련 작업에 사용할 DB 세션을 주입합니다.

        Args:
            db: 비동기 SQLAlchemy 세션.
        """
        self.db = db

    async def create_user(self, user_data: UserCreate) -> User:
        """
        Summary: 신규 사용자를 생성하고 기본 역할을 부여합니다.

        Contract:
            - username/email 중복 시 ValueError를 발생시킵니다.
            - 기본 역할("user")이 없으면 ValueError를 발생시킵니다.

        Args:
            user_data: 생성할 사용자 정보.

        Returns:
            User: 생성된 사용자 엔티티.

        Raises:
            ValueError: 중복 사용자/이메일 또는 기본 역할 누락.

        Side Effects:
            - DB 사용자 레코드 생성
        """
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
        """
        Summary: 사용자 목록을 최신순으로 조회합니다.

        Args:
            limit: 반환할 최대 개수(1 이상).
            offset: 시작 위치(0 이상).

        Returns:
            list[User]: 사용자 목록.

        Side Effects:
            - DB 조회
        """
        result = await self.db.execute(
            select(User).order_by(User.id.desc()).limit(limit).offset(offset)
        )
        return result.scalars().all()

    async def update_profile(self, *, user: User, data: UserUpdate) -> User:
        """
        Summary: 사용자 프로필(닉네임/이메일)을 갱신합니다.

        Contract:
            - 이메일 변경 시 중복 검사를 수행합니다.
            - 닉네임은 None이면 변경하지 않습니다.

        Args:
            user: 수정 대상 사용자 엔티티.
            data: 변경할 필드.

        Returns:
            User: 갱신된 사용자 엔티티.

        Raises:
            ValueError: 이메일 중복.

        Side Effects:
            - DB 사용자 레코드 업데이트
        """
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
        """
        Summary: 사용자의 비밀번호를 교체합니다.

        Contract:
            - 현재 비밀번호가 일치해야 변경됩니다.
            - 사용자 미존재 시 ValueError를 발생시킵니다.

        Args:
            user_id: 대상 사용자 ID.
            current_password: 현재 비밀번호.
            new_password: 새 비밀번호.

        Raises:
            ValueError: 사용자 미존재 또는 현재 비밀번호 불일치.

        Side Effects:
            - DB 사용자 레코드 업데이트
        """
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError("User not found")

        if not verify_password(current_password, user.password):
            raise ValueError("Invalid current password")

        user.password = hash_password(new_password)
        self.db.add(user)
        await self.db.commit()
