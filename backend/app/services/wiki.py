from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models import WikiPage, User
from app.schemas.wiki import WikiPageRead, WikiPageUpdate


class WikiService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_page(self, slug: str) -> WikiPageRead | None:
        page = await self.session.scalar(
            select(WikiPage)
            .options(selectinload(WikiPage.updated_by))
            .where(WikiPage.slug == slug)
        )
        if not page:
            return None

        return WikiPageRead(
            slug=page.slug,
            title=page.title,
            content=page.content,
            updated_at=page.updated_at,
            updated_by=getattr(page.updated_by, "username", None),
        )

    async def upsert_page(
        self, slug: str, data: WikiPageUpdate, *, user: User
    ) -> WikiPageRead:
        page = await self.session.scalar(
            select(WikiPage).where(WikiPage.slug == slug).with_for_update()
        )

        if page:
            if data.title is not None:
                page.title = data.title.strip()
            page.content = data.content
        else:
            title = data.title.strip() if data.title else slug
            page = WikiPage(
                slug=slug,
                title=title,
                content=data.content,
            )
            self.session.add(page)

        page.updated_by_id = user.id

        await self.session.commit()
        await self.session.refresh(page)

        updated = await self.session.scalar(
            select(WikiPage)
            .options(selectinload(WikiPage.updated_by))
            .where(WikiPage.id == page.id)
        )
        return WikiPageRead(
            slug=updated.slug,
            title=updated.title,
            content=updated.content,
            updated_at=updated.updated_at,
            updated_by=getattr(updated.updated_by, "username", None),
        )
