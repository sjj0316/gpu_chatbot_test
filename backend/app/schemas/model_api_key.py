from __future__ import annotations
from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class ModelApiKeyBase(BaseModel):
    alias: str | None = Field(default=None, max_length=50)
    provider_code: str = Field(min_length=1, max_length=32)
    model: str = Field(min_length=1, max_length=100)
    endpoint_url: str | None = Field(default=None, max_length=255)
    purpose_code: str = Field(min_length=1, max_length=32)
    is_public: bool = False
    is_active: bool = True
    extra: dict[str, Any] | None = None


class ModelApiKeyCreate(ModelApiKeyBase):
    api_key: str = Field(min_length=1)


class ModelApiKeyUpdate(BaseModel):
    alias: str | None = None
    provider_code: str | None = None
    model: str | None = None
    endpoint_url: str | None = None
    purpose_code: str | None = None
    is_public: bool | None = None
    is_active: bool | None = None
    extra: dict[str, Any] | None = None
    api_key: str | None = None


class ModelApiKeyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    alias: str | None
    provider_id: int
    provider_code: str | None = None
    model: str
    endpoint_url: str | None = None
    purpose_id: int
    purpose_code: str | None = None
    is_public: bool
    is_active: bool
    extra: dict[str, Any] | None
    owner_id: int
    owner_nickname: str | None = None
    created_at: datetime
    updated_at: datetime | None
    api_key_masked: str | None = None


class ModelApiKeyReadWithSecret(ModelApiKeyRead):
    api_key: str | None = None
