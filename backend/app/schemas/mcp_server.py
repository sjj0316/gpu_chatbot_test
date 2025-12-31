from __future__ import annotations

from typing import Any, Literal
from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
    field_validator,
    ValidationInfo,
    ConfigDict,
)

TransportLiteral = Literal["http", "streamable_http"]


class MCPToolInfo(BaseModel):
    name: str
    description: str | None = None
    input_schema: dict[str, Any] | None = None


class MCPServerRuntime(BaseModel):
    reachable: bool
    error: str | None = None
    tools: list[MCPToolInfo] = Field(default_factory=list)


class MCPServerConfig(BaseModel):
    """
    - transport: "http" | "streamable_http"
    - url: http(s) URL (HTTP 계열일 때 필수)
    """

    transport: TransportLiteral = Field(..., description="MCP 서버 전송 방식")
    url: HttpUrl | None = Field(None, description="HTTP/Streamable-HTTP 엔드포인트")

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )

    @field_validator("transport", mode="before")
    @classmethod
    def normalize_transport(cls, v: Any) -> str:
        s = (str(v or "")).strip().lower().replace("-", "_")
        if s not in ("http", "streamable_http"):
            raise ValueError("transport must be 'http' or 'streamable_http'")
        return s

    @field_validator("url")
    @classmethod
    def require_url_for_http(cls, v: HttpUrl | None, info: ValidationInfo):
        transport = info.data.get("transport")
        if transport in ("http", "streamable_http") and not v:
            raise ValueError("transport가 HTTP 계열이면 url은 필수입니다.")
        return v


class MCPServerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=1000)
    config: MCPServerConfig


class MCPServerCreate(MCPServerBase):
    pass


class MCPServerUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=1000)
    config: MCPServerConfig | None = None


class MCPServerRead(BaseModel):
    id: int
    name: str
    description: str | None
    config: dict[str, Any]
    runtime: MCPServerRuntime | None = None

    model_config = ConfigDict(from_attributes=True)
