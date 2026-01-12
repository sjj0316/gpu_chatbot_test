from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

if TYPE_CHECKING:
    from .user import User


class WikiPage(Base):
    __tablename__ = "wiki_pages"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    slug: Mapped[str] = mapped_column(sa.String(100), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(sa.String(200), nullable=False)
    content: Mapped[str] = mapped_column(sa.Text, nullable=False)
    is_public: Mapped[bool] = mapped_column(
        sa.Boolean, server_default=sa.text("true"), nullable=False, index=True
    )

    updated_by_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    updated_by: Mapped["User"] = relationship()

    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True), onupdate=sa.func.now()
    )
