"""Pydantic 스키마 정리"""

from app.schemas.user import UserCreate, UserRead
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    RefreshRequest,
)

from app.schemas.conversation_history import (
    ConversationHistoryCreate,
    ConversationHistoryRead,
)
from app.schemas.document import (
    ChunkItem,
    DocumentChunk,
    DocumentFile,
    PaginatedChunkResponse,
    PaginatedDocumentResponse,
    DocumentRead,
    DocumentDeleteRequest,
    DocumentUploadResponse,
    SearchQuery,
    SearchResult,
)
from app.schemas.collection import (
    CollectionCreate,
    CollectionUpdate,
    CollectionRead,
    PaginatedCollectionResponse,
)
from app.schemas.model_api_key import (
    ModelApiKeyCreate,
    ModelApiKeyUpdate,
    ModelApiKeyRead,
    ModelApiKeyReadWithSecret,
)
from app.schemas.conversation import (
    ConversationCreate,
    ConversationRead,
    ConversationListItem,
    HistoryItem,
    ChatRequest,
    ChatChunk,
    ChatResponse,
)
from app.schemas.mcp_server import (
    MCPServerConfig,
    MCPServerBase,
    MCPServerCreate,
    MCPServerUpdate,
    MCPServerRead,
    MCPToolInfo,
    MCPServerRuntime,
)

__all__ = [
    "UserCreate",
    "UserRead",
    "LoginRequest",
    "TokenResponse",
    "RefreshRequest",
    "ConversationCreate",
    "ConversationRead",
    "ConversationListItem",
    "HistoryItem",
    "ChatRequest",
    "ChatChunk",
    "ChatResponse",
    "ConversationHistoryCreate",
    "ConversationHistoryRead",
    "DocumentRead",
    "DocumentDeleteRequest",
    "DocumentUploadResponse",
    "PaginatedDocumentResponse",
    "CollectionCreate",
    "CollectionUpdate",
    "CollectionRead",
    "PaginatedCollectionResponse",
    "SearchQuery",
    "SearchResult",
    "ChunkItem",
    "DocumentChunk",
    "DocumentFile",
    "PaginatedChunkResponse",
    "ModelApiKeyCreate",
    "ModelApiKeyUpdate",
    "ModelApiKeyRead",
    "ModelApiKeyReadWithSecret",
    "MCPServerConfig",
    "MCPServerBase",
    "MCPServerCreate",
    "MCPServerUpdate",
    "MCPServerRead",
    "MCPToolInfo",
    "MCPServerRuntime",
]
