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
    description="사용자 소유의 문서 컬렉션을 생성합니다.",
    responses={
        401: {"description": "인증 실패"},
        409: {"description": "컬렉션 이름/제약 조건 충돌"},
        422: {"description": "요청 본문 검증 실패"},
        500: {"description": "서버 오류"},
    },
)
async def create_collection(
    db: SessionDep,
    user: CurrentUser,
    data: CollectionCreate,
):
    """
    Why: 문서와 임베딩을 묶어 관리할 논리적 단위를 생성합니다.

    Auth:
        - 필요: Bearer 토큰

    Request/Response:
        - 요청: 컬렉션 이름/설명/설정 값
        - 응답: 생성된 컬렉션 요약

    Errors:
        - 409: 동일 이름/제약 조건 충돌
        - 401/422: 인증 실패 또는 요청 형식 오류

    Side Effects:
        - DB 컬렉션 레코드 생성
    """
    service = CollectionService(db)
    return await service.create(user, data)


@router.get(
    "/",
    response_model=PaginatedCollectionResponse,
    summary="컬렉션 목록 조회",
    description="현재 사용자 소유 컬렉션을 페이지네이션으로 조회합니다.",
    responses={
        401: {"description": "인증 실패"},
        422: {"description": "쿼리 파라미터 검증 실패"},
        500: {"description": "서버 오류"},
    },
)
async def list_collections(
    db: SessionDep,
    user: CurrentUser,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    Why: 사용자가 보유한 컬렉션을 탐색/선택할 수 있게 합니다.

    Auth:
        - 필요: Bearer 토큰

    Request/Response:
        - 요청: limit/offset
        - 응답: 컬렉션 목록 + 페이지 정보

    Errors:
        - 401: 인증 실패
        - 422: 쿼리 파라미터가 범위를 벗어난 경우

    Side Effects:
        - 없음(조회 전용)
    """
    service = CollectionService(db)
    return await service.get_list(user, limit=limit, offset=offset)


@router.get(
    "/{collection_id}",
    response_model=CollectionRead,
    summary="컬렉션 상세 조회",
    description="컬렉션 상세 정보를 조회합니다.",
    responses={
        401: {"description": "인증 실패"},
        403: {"description": "접근 권한 없음"},
        404: {"description": "컬렉션이 존재하지 않음"},
        422: {"description": "경로 파라미터 검증 실패"},
        500: {"description": "서버 오류"},
    },
)
async def get_collection(
    collection_id: UUID,
    db: SessionDep,
    user: CurrentUser,
):
    """
    Why: 특정 컬렉션의 메타데이터를 확인합니다.

    Auth:
        - 필요: Bearer 토큰(소유자)

    Request/Response:
        - 요청: collection_id
        - 응답: 컬렉션 상세

    Errors:
        - 404: 컬렉션이 없거나 접근 불가한 경우
        - 401/422: 인증 실패 또는 경로 파라미터 오류

    Side Effects:
        - 없음(조회 전용)
    """
    service = CollectionService(db)
    return await service.get(collection_id, user)


@router.patch(
    "/{collection_id}",
    response_model=CollectionRead,
    summary="컬렉션 수정",
    description="컬렉션 이름/설정 값을 수정합니다.",
    responses={
        401: {"description": "인증 실패"},
        403: {"description": "수정 권한 없음"},
        404: {"description": "컬렉션이 존재하지 않음"},
        422: {"description": "요청 본문/경로 검증 실패"},
        500: {"description": "서버 오류"},
    },
)
async def update_collection(
    collection_id: UUID,
    data: CollectionUpdate,
    db: SessionDep,
    user: CurrentUser,
):
    """
    Why: 컬렉션 메타데이터 변경으로 운영 정책을 조정합니다.

    Auth:
        - 필요: Bearer 토큰(소유자)

    Request/Response:
        - 요청: 수정 가능한 필드
        - 응답: 수정된 컬렉션 상세

    Errors:
        - 404: 컬렉션이 없거나 접근 불가한 경우
        - 401/422: 인증 실패 또는 요청 형식 오류

    Side Effects:
        - DB 컬렉션 레코드 업데이트
    """
    service = CollectionService(db)
    return await service.update(collection_id, data, user)


@router.delete(
    "/{collection_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="컬렉션 삭제",
    description="컬렉션과 연관 리소스를 삭제합니다.",
    responses={
        401: {"description": "인증 실패"},
        403: {"description": "삭제 권한 없음"},
        404: {"description": "컬렉션이 존재하지 않음"},
        422: {"description": "경로 파라미터 검증 실패"},
        500: {"description": "서버 오류"},
    },
)
async def delete_collection(
    collection_id: UUID,
    *,
    db: SessionDep,
    user: CurrentUser,
):
    """
    Why: 더 이상 사용하지 않는 컬렉션을 제거합니다.

    Auth:
        - 필요: Bearer 토큰(소유자)

    Request/Response:
        - 요청: collection_id
        - 응답: 없음(204)

    Errors:
        - 404: 컬렉션이 없거나 접근 불가한 경우
        - 401/422: 인증 실패 또는 경로 파라미터 오류

    Side Effects:
        - DB 컬렉션 삭제 및 관련 문서/벡터 정리
    """
    service = CollectionService(db)
    await service.delete(collection_id, user)


@router.post(
    "/{collection_id}/documents",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="문서 업로드",
    description="컬렉션에 문서를 업로드하고 임베딩/벡터스토어에 저장합니다.",
    responses={
        400: {"description": "메타데이터 형식 오류 또는 파일/메타데이터 불일치"},
        401: {"description": "인증 실패"},
        403: {"description": "접근 권한 없음"},
        404: {"description": "컬렉션이 존재하지 않음"},
        422: {"description": "요청 형식 검증 실패"},
        500: {"description": "서버 오류"},
    },
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
    """
    Why: 파일을 컬렉션에 적재하고 검색을 위한 임베딩을 생성합니다.

    Auth:
        - 필요: Bearer 토큰(소유자)

    Request/Response:
        - 요청: files + (선택) metadatas_json/chunk_size/chunk_overlap/model_api_key_id
        - 응답: 업로드 결과 요약(성공/실패 수, 저장된 문서 정보)

    Errors:
        - 400: 메타데이터 JSON 파싱 실패 또는 파일 수 불일치
        - 403/404: 권한 없음 또는 컬렉션 미존재
        - 401/422: 인증 실패 또는 요청 형식 오류

    Side Effects:
        - 파일/문서 메타데이터 저장
        - 임베딩 생성 및 벡터스토어 저장
    """
    if not metadatas_json:
        metadatas: list[dict] | list[None] = [None] * len(files)
    else:
        try:
            metadatas = _metadata_adapter.validate_json(metadatas_json)
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=e.errors()) from e
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
    description="컬렉션에 등록된 문서/청크 목록을 조회합니다.",
    responses={
        401: {"description": "인증 실패"},
        403: {"description": "접근 권한 없음"},
        404: {"description": "컬렉션이 존재하지 않음"},
        422: {"description": "쿼리 파라미터 검증 실패"},
        500: {"description": "서버 오류"},
    },
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
    """
    Why: 문서 단위 또는 청크 단위로 컬렉션 콘텐츠를 확인합니다.

    Auth:
        - 필요: Bearer 토큰(소유자)

    Request/Response:
        - 요청: limit/offset/view(document|chunk)
        - 응답: 문서 또는 청크 목록 + 페이지 정보

    Errors:
        - 403/404: 권한 없음 또는 컬렉션 미존재
        - 401/422: 인증 실패 또는 쿼리 파라미터 오류

    Side Effects:
        - 없음(조회 전용)
    """
    service = DocumentService(db, collection_id, user)
    return await service.get_list(limit=limit, offset=offset, view=view)


@router.delete(
    "/{collection_id}/documents",
    status_code=204,
    summary="컬렉션 문서 삭제",
    description="컬렉션의 모든 문서를 삭제하거나 file_ids/document_ids 기준으로 선택 삭제합니다.",
    responses={
        401: {"description": "인증 실패"},
        403: {"description": "접근 권한 없음"},
        404: {"description": "삭제 대상 없음"},
        422: {"description": "요청 본문 검증 실패"},
        500: {"description": "서버 오류"},
    },
)
async def delete_documents(
    collection_id: UUID,
    data: DocumentDeleteRequest,
    db: SessionDep,
    user: CurrentUser,
):
    """
    Why: 컬렉션 내 불필요한 문서를 일괄 또는 선택 삭제합니다.

    Auth:
        - 필요: Bearer 토큰(소유자)

    Request/Response:
        - 요청: file_ids 또는 document_ids
        - 응답: 없음(204)

    Errors:
        - 404: 삭제 대상이 없는 경우
        - 401/422: 인증 실패 또는 요청 형식 오류

    Side Effects:
        - DB 문서/청크 삭제
        - 벡터스토어 데이터 제거
    """
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
    responses={
        401: {"description": "인증 실패"},
        403: {"description": "접근 권한 없음"},
        404: {"description": "삭제 대상 없음"},
        422: {"description": "경로/쿼리 파라미터 검증 실패"},
        500: {"description": "서버 오류"},
    },
)
async def delete_document_by_id(
    collection_id: UUID,
    target_id: UUID,
    *,
    delete_by: Literal["file_id", "document_id"] = Query(...),
    db: SessionDep,
    user: CurrentUser,
):
    """
    Why: 문서 식별자를 기반으로 개별 문서를 제거합니다.

    Auth:
        - 필요: Bearer 토큰(소유자)

    Request/Response:
        - 요청: target_id + delete_by
        - 응답: 없음(204)

    Errors:
        - 404: 삭제 대상이 없는 경우
        - 401/422: 인증 실패 또는 파라미터 오류

    Side Effects:
        - DB 문서/청크 삭제
        - 벡터스토어 데이터 제거
    """
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
    responses={
        401: {"description": "인증 실패"},
        403: {"description": "접근 권한 없음"},
        404: {"description": "컬렉션이 존재하지 않음"},
        422: {"description": "요청 본문 검증 실패"},
        500: {"description": "서버 오류"},
    },
)
async def search_documents(
    collection_id: UUID,
    search: SearchQuery,
    db: SessionDep,
    user: CurrentUser,
):
    """
    Why: 컬렉션의 문서/청크를 의미 기반으로 조회합니다.

    Auth:
        - 필요: Bearer 토큰(소유자)

    Request/Response:
        - 요청: query/limit/filter/search_type/model_api_key_id
        - 응답: 검색 결과 목록(점수/메타데이터 포함)

    Errors:
        - 403/404: 권한 없음 또는 컬렉션 미존재
        - 401/422: 인증 실패 또는 요청 형식 오류

    Side Effects:
        - 없음(조회 전용)
    """
    service = DocumentService(db, collection_id, user)
    return await service.search(
        query=search.query,
        limit=search.limit or 10,
        filter=search.filter,
        search_type=search.search_type,
        model_api_key_id=search.model_api_key_id,
    )
