from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

if TYPE_CHECKING:
    from .user import User
    from .conversation_history import ConversationHistory
    from .mcp_server import MCPServer
    from .model_api_key import ModelApiKey

conversation_mcp_server = sa.Table(
    "conversation_mcp_server",
    Base.metadata,
    sa.Column(
        "conversation_id",
        sa.Integer,
        sa.ForeignKey("conversations.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    sa.Column(
        "mcp_server_id",
        sa.Integer,
        sa.ForeignKey("mcp_servers.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Conversation(Base):
    __tablename__ = "conversations"
    __table_args__ = (sa.Index("ix_conv_user_created", "user_id", "created_at"),)

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user: Mapped["User"] = relationship(back_populates="conversations")

    title: Mapped[str | None] = mapped_column(sa.String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True), onupdate=sa.func.now()
    )

    default_model_key_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey("model_api_keys.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    default_model_key: Mapped["ModelApiKey | None"] = relationship()
    default_params: Mapped[dict | None] = mapped_column(sa.JSON, nullable=True)

    histories: Mapped[list["ConversationHistory"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
    )

    mcp_servers: Mapped[list["MCPServer"]] = relationship(
        secondary=conversation_mcp_server,
        back_populates="conversations",
    )
