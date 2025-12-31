from fastapi import APIRouter

from app.routers.auth import router as auth_router
from app.routers.user import router as user_router
from app.routers.conversations import router as conversation_router
from app.routers.rag import router as rag_router
from app.routers.model_api_keys import router as model_api_key_router
from app.routers.mcp_server import router as mcp_server_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(user_router)
api_router.include_router(conversation_router)
api_router.include_router(rag_router)
api_router.include_router(model_api_key_router)
api_router.include_router(mcp_server_router)

api_tags = [
    {"name": "Auth", "description": "인증 및 로그인 관련 API"},
    {"name": "User", "description": "사용자 API"},
    {"name": "Conversation", "description": "대화 및 대화 이력 API"},
    {"name": "RAG", "description": "RAG 용 컬렉션, 문서 API"},
    {"name": "API Keys", "description": "모델 호출을 위한 API KEY 관리"},
    {"name": "MCP Servers", "description": "MCP 서버 관리"},
]

__all__ = ["api_router", "api_tags"]
