from fastapi import APIRouter, HTTPException

from app.dependencies import SessionDep, CurrentUser
from app.schemas import WikiPageRead, WikiPageUpdate
from app.services.wiki import WikiService

router = APIRouter(prefix="/wiki", tags=["Wiki"])


@router.get("/{slug}", response_model=WikiPageRead)
async def get_wiki_page(slug: str, db: SessionDep):
    service = WikiService(db)
    page = await service.get_page(slug)
    if not page:
        raise HTTPException(status_code=404, detail="페이지를 찾을 수 없습니다.")
    return page


@router.put("/{slug}", response_model=WikiPageRead)
async def upsert_wiki_page(slug: str, payload: WikiPageUpdate, db: SessionDep, user: CurrentUser):
    service = WikiService(db)
    return await service.upsert_page(slug, payload, user=user)
