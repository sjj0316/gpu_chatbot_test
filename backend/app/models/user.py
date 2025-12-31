from __future__ import annotations
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


if TYPE_CHECKING:
    from .conversation import Conversation
    from .model_api_key import ModelApiKey
    from .lookups import UserRoleLkp


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    username: Mapped[str] = mapped_column(sa.String(50), unique=True, index=True)
    password: Mapped[str] = mapped_column(sa.String(128))
    nickname: Mapped[str | None] = mapped_column(sa.String(50))
    email: Mapped[str] = mapped_column(sa.String(100), unique=True, index=True)

    role_id: Mapped[int] = mapped_column(
        sa.ForeignKey("user_roles.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    role: Mapped["UserRoleLkp"] = relationship()

    conversations: Mapped[list["Conversation"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    model_api_keys: Mapped[list["ModelApiKey"]] = relationship(
        back_populates="owner", cascade="all, delete-orphan"
    )
