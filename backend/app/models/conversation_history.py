from __future__ import annotations
import enum
from typing import TYPE_CHECKING

from datetime import datetime
from decimal import Decimal
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

if TYPE_CHECKING:
    from .conversation import Conversation
    from .mcp_server import MCPServer


class MessageRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"
    SYSTEM = "system"


class MessageStatus(str, enum.Enum):
    SUCCESS = "success"
    ERROR = "error"
    CANCELLED = "cancelled"


if TYPE_CHECKING:
    from .conversation import Conversation
    from .mcp_server import MCPServer
    from .model_api_key import ModelApiKey
    from .lookups import MessageRoleLkp, MessageStatusLkp, ModelProviderLkp


class ConversationHistory(Base):
    __tablename__ = "conversation_histories"
    __table_args__ = (
        sa.Index("ix_hist_conv_ts", "conversation_id", "timestamp"),
        sa.Index("ix_hist_model_key", "model_api_key_id"),
        sa.Index("ix_hist_mcp", "mcp_server_id"),
        sa.Index("ix_hist_tool_call", "conversation_id", "tool_call_id"),
    )

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)

    conversation_id: Mapped[int] = mapped_column(
        sa.ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    conversation: Mapped["Conversation"] = relationship(back_populates="histories")

    role_id: Mapped[int] = mapped_column(
        sa.ForeignKey("message_roles.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    role: Mapped["MessageRoleLkp"] = relationship(lazy="raise")

    content: Mapped[str] = mapped_column(sa.Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
    )

    mcp_server_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey("mcp_servers.id", ondelete="SET NULL")
    )
    mcp_server: Mapped["MCPServer | None"] = relationship(lazy="raise")

    model_api_key_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey("model_api_keys.id", ondelete="SET NULL")
    )
    model_api_key: Mapped["ModelApiKey | None"] = relationship(lazy="raise")

    model_provider_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey("model_providers.id", ondelete="SET NULL")
    )
    model_provider: Mapped["ModelProviderLkp | None"] = relationship(lazy="raise")
    model_provider_code: Mapped[str | None] = mapped_column(sa.String(32))
    model_model: Mapped[str | None] = mapped_column(sa.String(100))
    params: Mapped[dict | None] = mapped_column(sa.JSON)

    input_tokens: Mapped[int | None] = mapped_column(sa.Integer)
    output_tokens: Mapped[int | None] = mapped_column(sa.Integer)
    cost: Mapped[Decimal | None] = mapped_column(sa.Numeric(18, 6))
    latency_ms: Mapped[int | None] = mapped_column(sa.Integer)

    status_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey("message_statuses.id", ondelete="SET NULL"), index=True
    )
    status: Mapped["MessageStatusLkp | None"] = relationship(lazy="raise")
    error: Mapped[str | None] = mapped_column(sa.Text)

    tool_name: Mapped[str | None] = mapped_column(sa.String(256))
    tool_call_id: Mapped[str | None] = mapped_column(sa.String(64))
    tool_input: Mapped[dict | None] = mapped_column(sa.JSON)
    tool_output: Mapped[dict | None] = mapped_column(sa.JSON)
