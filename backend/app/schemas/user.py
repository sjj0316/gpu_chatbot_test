from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreate(BaseModel):
    username: str
    password: str
    nickname: str
    email: EmailStr


class UserRead(BaseModel):
    id: int
    username: str
    nickname: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    nickname: str | None = None
    email: EmailStr | None = None
