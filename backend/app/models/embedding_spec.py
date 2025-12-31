from __future__ import annotations
from typing import TYPE_CHECKING

from datetime import datetime
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

if TYPE_CHECKING:
    from .lookups import ModelProviderLkp


class EmbeddingSpec(Base):
    __tablename__ = "embedding_specs"
    __table_args__ = (
        sa.UniqueConstraint(
            "provider_id", "model", name="uq_embed_spec_provider_model"
        ),
        sa.CheckConstraint("dimension > 0", name="ck_embed_spec_dimension_pos"),
        sa.Index("ix_embed_spec_provider_model", "provider_id", "model"),
        sa.Index("ix_embed_spec_active", "is_active"),
    )

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    provider_id: Mapped[int] = mapped_column(
        sa.ForeignKey("model_providers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    provider: Mapped["ModelProviderLkp"] = relationship()
    model: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    dimension: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    dtype: Mapped[str | None] = mapped_column(sa.String(16))
    notes: Mapped[str | None] = mapped_column(sa.Text)
    is_active: Mapped[bool] = mapped_column(
        sa.Boolean, server_default=sa.text("true"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True), onupdate=sa.func.now()
    )
