from fastapi import APIRouter, HTTPException

from app.dependencies import SessionDep, CurrentUser
from app.schemas import WikiPageRead, WikiPageUpdate
from app.services.wiki import WikiService

router = APIRouter(prefix="/wiki", tags=["Wiki"])


@router.get(
    "/{slug}",
    response_model=WikiPageRead,
    summary="위키 페이지 조회",
    description="슬러그 기준으로 위키 페이지를 조회합니다.",
    responses={
        404: {"description": "페이지 없음"},
        422: {"description": "경로 파라미터 검증 실패"},
        500: {"description": "서버 오류"},
    },
)
async def get_wiki_page(slug: str, db: SessionDep):
    """
    Why: 문서형 도움말/정책을 UI에서 조회할 수 있게 합니다.

    Auth:
        - 필요 없음(읽기 전용 공개)

    Request/Response:
        - 요청: slug
        - 응답: 위키 페이지 콘텐츠/메타데이터

    Errors:
        - 404: 페이지가 존재하지 않는 경우
        - 422: 경로 파라미터가 유효하지 않은 경우

    Side Effects:
        - 없음(조회 전용)
    """
    service = WikiService(db)
    page = await service.get_page(slug)
    if not page:
        raise HTTPException(status_code=404, detail="페이지를 찾을 수 없습니다.")
    return page


@router.put(
    "/{slug}",
    response_model=WikiPageRead,
    summary="위키 페이지 생성/수정",
    description="슬러그 기준으로 페이지를 생성하거나 갱신합니다.",
    responses={
        401: {"description": "인증 실패"},
        403: {"description": "권한 없음"},
        422: {"description": "요청 본문/경로 검증 실패"},
        500: {"description": "서버 오류"},
    },
)
async def upsert_wiki_page(
    slug: str, payload: WikiPageUpdate, db: SessionDep, user: CurrentUser
):
    """
    Why: 운영자가 위키 콘텐츠를 즉시 갱신할 수 있도록 합니다.

    Auth:
        - 필요: Bearer 토큰(권한 보유자)

    Request/Response:
        - 요청: slug + 업데이트 본문
        - 응답: 생성/갱신된 페이지

    Errors:
        - 401/422: 인증 실패 또는 요청 형식 오류
        - 403: 권한 부족

    Side Effects:
        - DB 위키 페이지 생성 또는 업데이트
    """
    service = WikiService(db)
    return await service.upsert_page(slug, payload, user=user)
