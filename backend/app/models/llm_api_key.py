from __future__ import annotations
from typing import TYPE_CHECKING, Any
from datetime import datetime
import enum

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship, deferred

from app.db import Base

if TYPE_CHECKING:
    from .user import User


class LLMProvider(str, enum.Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    MISTRAL = "mistral"
    AZURE_OPENAI = "azure_openai"
    GROQ = "groq"
    LOCAL = "local"
    OTHER = "other"


class LLMPurpose(str, enum.Enum):
    CHAT = "chat"
    EMBEDDING = "embedding"


class LLMApiKey(Base):
    __tablename__ = "llm_api_keys"
    __table_args__ = (
        sa.UniqueConstraint("owner_id", "alias", name="uq_llmkey_owner_alias"),
        sa.UniqueConstraint(
            "owner_id",
            "provider",
            "model",
            "endpoint_url",
            name="uq_llmkey_owner_provider_model_endpoint",
        ),
        sa.Index("ix_llmkey_public_active", "is_public", "is_active"),
        sa.Index("ix_llmkey_provider_purpose", "provider", "purpose"),
    )

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    alias: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)
    provider: Mapped[LLMProvider] = mapped_column(
        sa.Enum(LLMProvider, name="llm_provider"), nullable=False
    )
    model: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    endpoint_url: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    purpose: Mapped[LLMPurpose] = mapped_column(
        sa.Enum(LLMPurpose, name="llm_purpose"), nullable=False
    )

    # 기본 조회에서 제외 - DB 보안 처리 필요 (암호화?)
    api_key: Mapped[str] = deferred(mapped_column(sa.Text, nullable=False))
    is_public: Mapped[bool] = mapped_column(
        sa.Boolean, server_default=sa.text("false"), nullable=False, index=True
    )
    is_active: Mapped[bool] = mapped_column(
        sa.Boolean, server_default=sa.text("true"), nullable=False, index=True
    )
    extra: Mapped[dict[str, Any] | None] = mapped_column(sa.JSON, nullable=True)
    owner_id: Mapped[int] = mapped_column(
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    owner: Mapped["User"] = relationship(back_populates="llm_api_keys")
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True), onupdate=sa.func.now()
    )

    __mapper_args__ = {"eager_defaults": True}
