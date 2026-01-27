from __future__ import annotations
from typing import TYPE_CHECKING

from datetime import datetime
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship, deferred

from app.db import Base

if TYPE_CHECKING:
    from .user import User
    from .lookups import ModelProviderLkp, ModelPurposeLkp


class ModelApiKey(Base):
    __tablename__ = "model_api_keys"
    __table_args__ = (
        sa.UniqueConstraint(
            "owner_id",
            "provider_id",
            "model",
            "purpose_id",
            name="uq_modelkey_owner_provider_model_purpose",
        ),
        sa.UniqueConstraint("owner_id", "alias", name="uq_modelkey_owner_alias"),
        sa.Index("ix_modelkey_public_active", "is_public", "is_active"),
        sa.Index("ix_modelkey_provider_purpose", "provider_id", "purpose_id"),
    )

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    alias: Mapped[str | None] = mapped_column(sa.String(50))

    provider_id: Mapped[int] = mapped_column(
        sa.ForeignKey("model_providers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    provider: Mapped["ModelProviderLkp"] = relationship()
    model: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    endpoint_url: Mapped[str | None] = mapped_column(sa.String(255))

    purpose_id: Mapped[int] = mapped_column(
        sa.ForeignKey("model_purposes.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    purpose: Mapped["ModelPurposeLkp"] = relationship()

    api_key: Mapped[str] = deferred(mapped_column(sa.Text, nullable=False))

    is_public: Mapped[bool] = mapped_column(
        sa.Boolean, server_default=sa.text("false"), nullable=False, index=True
    )
    is_active: Mapped[bool] = mapped_column(
        sa.Boolean, server_default=sa.text("true"), nullable=False, index=True
    )

    extra: Mapped[dict | None] = mapped_column(sa.JSON)

    owner_id: Mapped[int] = mapped_column(
        sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    owner: Mapped["User"] = relationship()

    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True), onupdate=sa.func.now()
    )
