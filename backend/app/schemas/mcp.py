from __future__ import annotations
from typing import Literal
from pydantic import BaseModel


class MCPServerRead(BaseModel):
    id: int
    name: str
    description: str | None = None
    config: dict


class MCPServerCreate(BaseModel):
    name: str
    description: str | None = None
    transport: Literal["streamable_http", "sse"]
    url: str
    headers: dict[str, str] | None = None
