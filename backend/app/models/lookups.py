from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base


class UserRoleLkp(Base):
    __tablename__ = "user_roles"
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    code: Mapped[str] = mapped_column(
        sa.String(32), unique=True, nullable=False, index=True
    )
    label: Mapped[str | None] = mapped_column(sa.String(64))
    is_active: Mapped[bool] = mapped_column(
        sa.Boolean, server_default=sa.text("true"), nullable=False
    )


class ModelProviderLkp(Base):
    __tablename__ = "model_providers"
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    code: Mapped[str] = mapped_column(
        sa.String(32), unique=True, nullable=False, index=True
    )
    label: Mapped[str | None] = mapped_column(sa.String(64))
    is_active: Mapped[bool] = mapped_column(
        sa.Boolean, server_default=sa.text("true"), nullable=False
    )


class ModelPurposeLkp(Base):
    __tablename__ = "model_purposes"
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    code: Mapped[str] = mapped_column(
        sa.String(32), unique=True, nullable=False, index=True
    )
    label: Mapped[str | None] = mapped_column(sa.String(64))
    is_active: Mapped[bool] = mapped_column(
        sa.Boolean, server_default=sa.text("true"), nullable=False
    )


class MessageRoleLkp(Base):
    __tablename__ = "message_roles"
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    code: Mapped[str] = mapped_column(
        sa.String(32), unique=True, nullable=False, index=True
    )
    label: Mapped[str | None] = mapped_column(sa.String(64))
    is_active: Mapped[bool] = mapped_column(
        sa.Boolean, server_default=sa.text("true"), nullable=False
    )


class MessageStatusLkp(Base):
    __tablename__ = "message_statuses"
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    code: Mapped[str] = mapped_column(
        sa.String(32), unique=True, nullable=False, index=True
    )
    label: Mapped[str | None] = mapped_column(sa.String(64))
    is_active: Mapped[bool] = mapped_column(
        sa.Boolean, server_default=sa.text("true"), nullable=False
    )
