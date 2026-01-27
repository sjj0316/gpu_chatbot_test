from __future__ import annotations
from typing import Any, Literal
from uuid import UUID
from pydantic import BaseModel, Field


class ConversationCreate(BaseModel):
    title: str | None = None
    default_model_key_id: int | None = None
    default_params: dict[str, Any] | None = None
    mcp_server_ids: list[int] | None = None


class ConversationRead(BaseModel):
    id: int
    title: str | None = None


class ConversationListItem(BaseModel):
    id: int
    title: str | None = None


class HistoryItem(BaseModel):
    id: int
    role: Literal["system", "user", "assistant", "tool"]
    content: str | None = None
    timestamp: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    cost: float | None = None
    latency_ms: int | None = None
    tool_name: str | None = None
    tool_call_id: str | None = None
    tool_input: dict | list | str | None = None
    tool_output: dict | list | str | None = None
    error: str | None = None


class RagRequest(BaseModel):
    collection_id: UUID
    query: str | None = None
    limit: int | None = 10
    model_api_key_id: int | None = 1
    filter: dict[str, Any] | None = None
    search_type: Literal["semantic", "keyword", "hybrid"] = "semantic"


class ChatRequest(BaseModel):
    conversation_id: int | None = None
    message: str = Field(..., min_length=1)
    model_key_id: int | None = None
    params: dict[str, Any] | None = None
    system_prompt: str | None = None
    mcp_server_ids: list[int] | None = None
    rag: RagRequest | None = None


class ChatChunk(BaseModel):
    type: Literal["token", "update", "done", "error"]
    data: dict


class ChatResponse(BaseModel):
    conversation_id: int
    message_id: int
    content: str
