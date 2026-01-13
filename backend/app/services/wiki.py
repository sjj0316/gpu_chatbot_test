from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models import WikiPage, User
from app.schemas.wiki import WikiPageRead, WikiPageUpdate


class WikiService:
    def __init__(self, session: AsyncSession):
        """
        Why: 위키 페이지 작업에 사용할 DB 세션을 주입합니다.

        Args:
            session: 비동기 SQLAlchemy 세션.
        """
        self.session = session

    async def get_page(self, slug: str) -> WikiPageRead | None:
        """
        Summary: 슬러그로 위키 페이지를 조회합니다.

        Args:
            slug: 페이지 슬러그.

        Returns:
            WikiPageRead | None: 페이지 DTO 또는 None.

        Side Effects:
            - DB 조회
        """
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
        """
        Summary: 슬러그 기준으로 페이지를 생성 또는 갱신합니다.

        Contract:
            - 페이지가 없으면 새로 생성합니다.
            - updated_by_id를 항상 갱신합니다.

        Args:
            slug: 페이지 슬러그.
            data: 업데이트 요청 데이터.
            user: 수정 사용자.

        Returns:
            WikiPageRead: 갱신된 페이지 DTO.

        Side Effects:
            - DB 레코드 생성/수정
        """
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
