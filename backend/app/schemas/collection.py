from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class CollectionCreate(BaseModel):
    name: str
    description: str | None = None
    is_public: bool | None = False
    model_api_key_id: int | None = 1


class CollectionUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    is_public: bool | None = None


class CollectionRead(BaseModel):
    collection_id: UUID  # langchain_pg_collection.uuid
    table_id: str
    name: str
    description: str | None = None
    embedding_id: int | None = None
    embedding_dimension: int | None = None
    embedding_model: str | None = None
    is_public: bool
    owner_id: int
    document_count: int
    chunk_count: int


class PaginatedCollectionResponse(BaseModel):
    total_count: int
    items: list[CollectionRead]
