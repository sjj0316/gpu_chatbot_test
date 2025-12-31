from __future__ import annotations
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import String, Boolean
from uuid import uuid4

from app.db import Base

if TYPE_CHECKING:
    from .embedding_spec import EmbeddingSpec


class Collection(Base):
    __tablename__ = "collections"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String)
    is_public: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    owner_id: Mapped[str] = mapped_column(String, nullable=False)
    embedding_id: Mapped[int] = mapped_column(
        sa.ForeignKey("embedding_specs.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    embedding: Mapped["EmbeddingSpec"] = relationship()

    @property
    def table_name(self) -> str:
        return f"collection_{str(self.id).replace('-', '_')}"
