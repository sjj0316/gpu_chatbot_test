from pydantic import BaseModel
from typing import Any, Literal


class ChunkItem(BaseModel):
    id: str
    content: str
    metadata: dict[str, Any]
    source: str | None = None


class DocumentChunk(BaseModel):
    id: str
    content: str
    metadata: dict[str, Any]
    collection_id: str


class DocumentFile(BaseModel):
    file_id: str
    source: str
    chunk_count: int
    chunks: list[ChunkItem]


class PaginatedChunkResponse(BaseModel):
    items: list[ChunkItem]
    chunk_total: int
    file_total: int


class PaginatedDocumentResponse(BaseModel):
    items: list[DocumentFile]
    chunk_total: int
    file_total: int


class DocumentRead(BaseModel):
    file_id: str
    file_name: str
    chunk_count: int


class DocumentDeleteRequest(BaseModel):
    file_ids: list[str] | None = None
    document_ids: list[str] | None = None


class DocumentUploadResponse(BaseModel):
    success: bool
    message: str
    added_chunk_ids: list[str]
    warnings: list[str] | None = None


class SearchQuery(BaseModel):
    query: str
    limit: int | None = 10
    model_api_key_id: int | None = 1
    filter: dict[str, Any] | None = None
    search_type: Literal["semantic", "keyword", "hybrid"] = "semantic"


class SearchResult(BaseModel):
    id: str
    page_content: str
    metadata: dict[str, Any]
    score: float | None = None
