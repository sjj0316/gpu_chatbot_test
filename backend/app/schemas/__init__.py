"""Pydantic 스키마 정리"""

from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    RefreshRequest,
    ChangePasswordRequest,
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
    RagRequest,
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
from app.schemas.wiki import WikiPageRead, WikiPageUpdate

__all__ = [
    "UserCreate",
    "UserRead",
    "UserUpdate",
    "LoginRequest",
    "TokenResponse",
    "RefreshRequest",
    "ChangePasswordRequest",
    "ConversationCreate",
    "ConversationRead",
    "ConversationListItem",
    "HistoryItem",
    "RagRequest",
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
    "WikiPageRead",
    "WikiPageUpdate",
]
