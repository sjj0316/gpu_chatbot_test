from typing import Any, Literal
from uuid import UUID
from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Query,
    File,
    Form,
    UploadFile,
    Response,
)
from pydantic import TypeAdapter, ValidationError

from app.dependencies import SessionDep, CurrentUser
from app.services import CollectionService, DocumentService
from app.schemas import (
    CollectionCreate,
    CollectionRead,
    CollectionUpdate,
    PaginatedCollectionResponse,
    PaginatedDocumentResponse,
    DocumentUploadResponse,
    DocumentDeleteRequest,
    PaginatedChunkResponse,
    SearchQuery,
    SearchResult,
)

_metadata_adapter = TypeAdapter(list[dict[str, Any]])

router = APIRouter(prefix="/collections", tags=["RAG"])


@router.post(
    "/",
    response_model=CollectionRead,
    status_code=status.HTTP_201_CREATED,
    summary="컬렉션 생성",
    description="컬렉션을 생성합니다.",
)
async def create_collection(
    db: SessionDep,
    user: CurrentUser,
    data: CollectionCreate,
):
    service = CollectionService(db)
    return await service.create(user, data)


@router.get(
    "/",
    response_model=PaginatedCollectionResponse,
    summary="컬렉션 목록 조회",
    description="컬렉션 목록을 조회합니다.",
)
async def list_collections(
    db: SessionDep,
    user: CurrentUser,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    service = CollectionService(db)
    return await service.get_list(user, limit=limit, offset=offset)


@router.get(
    "/{collection_id}",
    response_model=CollectionRead,
    summary="컬렉션 상세 조회",
    description="컬렉션을 상세 조회합니다.",
)
async def get_collection(
    collection_id: UUID,
    db: SessionDep,
    user: CurrentUser,
):
    service = CollectionService(db)
    return await service.get(collection_id, user)


@router.patch(
    "/{collection_id}",
    response_model=CollectionRead,
    summary="컬렉션 수정",
    description="컬렉션을 수정합니다.",
)
async def update_collection(
    collection_id: UUID,
    data: CollectionUpdate,
    db: SessionDep,
    user: CurrentUser,
):
    service = CollectionService(db)
    return await service.update(collection_id, data, user)


@router.delete(
    "/{collection_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="컬렉션 삭제",
    description="컬렉션을 삭제합니다.",
)
async def delete_collection(
    collection_id: UUID,
    *,
    db: SessionDep,
    user: CurrentUser,
):
    service = CollectionService(db)
    await service.delete(collection_id, user)


@router.post(
    "/{collection_id}/documents",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="문서 업로드",
    description="문서를 업로드 합니다.",
)
async def create_documents(
    collection_id: UUID,
    *,
    files: list[UploadFile] = File(...),
    metadatas_json: str | None = Form(None),
    chunk_size: int = Form(1000),
    chunk_overlap: int = Form(200),
    model_api_key_id: int = Form(1),
    db: SessionDep,
    user: CurrentUser,
):
    if not metadatas_json:
        metadatas: list[dict] | list[None] = [None] * len(files)
    else:
        try:
            metadatas = _metadata_adapter.validate_json(metadatas_json)
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=e.errors())
        if len(metadatas) != len(files):
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Number of metadata objects ({len(metadatas)}) "
                    f"does not match number of files ({len(files)})."
                ),
            )
    service = DocumentService(db, collection_id, user)
    return await service.create(
        files, metadatas, chunk_size, chunk_overlap, model_api_key_id
    )


@router.get(
    "/{collection_id}/documents",
    response_model=PaginatedDocumentResponse | PaginatedChunkResponse,
    summary="컬렉션 내 문서 목록 조회",
    description="컬렉션에 등록된 문서 목록을 조회합니다.",
)
async def list_documents(
    collection_id: UUID,
    *,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    view: Literal["document", "chunk"] = Query("document"),
    db: SessionDep,
    user: CurrentUser,
):
    service = DocumentService(db, collection_id, user)
    return await service.get_list(limit=limit, offset=offset, view=view)


@router.delete(
    "/{collection_id}/documents",
    status_code=204,
    summary="컬렉션 문서 삭제",
    description="컬렉션의 모든 문서를 삭제하거나 file_ids/document_ids 기준으로 선택 삭제합니다.",
)
async def delete_documents(
    collection_id: UUID,
    data: DocumentDeleteRequest,
    db: SessionDep,
    user: CurrentUser,
):
    service = DocumentService(db, collection_id, user)
    deleted = await service.delete_all(
        file_ids=data.file_ids, document_ids=data.document_ids
    )
    if deleted == 0:
        raise HTTPException(status_code=404, detail="삭제된 문서가 없습니다.")
    return Response(status_code=204)


@router.delete(
    "/{collection_id}/documents/{target_id}",
    status_code=204,
    summary="단일 문서 삭제",
    description="file_id 또는 document_id로 단일 문서를 삭제합니다.",
)
async def delete_document_by_id(
    collection_id: UUID,
    target_id: UUID,
    *,
    delete_by: Literal["file_id", "document_id"] = Query(...),
    db: SessionDep,
    user: CurrentUser,
):
    service = DocumentService(db, collection_id, user)
    deleted = await service.delete_by(target_id, delete_by)
    if deleted == 0:
        raise HTTPException(status_code=404, detail="삭제된 문서가 없습니다.")
    return Response(status_code=204)


@router.post(
    "/{collection_id}/documents/search",
    response_model=list[SearchResult],
    summary="문서 검색",
    description="컬렉션 내 문서를 semantic, keyword, hybrid 방식으로 검색합니다.",
)
async def search_documents(
    collection_id: UUID,
    search: SearchQuery,
    db: SessionDep,
    user: CurrentUser,
):
    service = DocumentService(db, collection_id, user)
    return await service.search(
        query=search.query,
        limit=search.limit or 10,
        filter=search.filter,
        search_type=search.search_type,
        model_api_key_id=search.model_api_key_id,
    )
