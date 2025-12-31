from __future__ import annotations
from typing import TYPE_CHECKING

from typing import Any
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

if TYPE_CHECKING:
    from .conversation import Conversation


class MCPServer(Base):
    __tablename__ = "mcp_servers"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(sa.String, nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(sa.String, nullable=True)
    config: Mapped[dict[str, Any]] = mapped_column(sa.JSON, nullable=False)
    # config 예시:
    # {
    #   "transport": "streamable_http",
    #   "url": "http://localhost:8000/mcp",
    # }

    # Conversation ↔ MCPServer 다대다
    conversations: Mapped[list["Conversation"]] = relationship(
        secondary="conversation_mcp_server",
        back_populates="mcp_servers",
    )
