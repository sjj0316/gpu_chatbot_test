from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import ConversationHistory
from app.schemas import ConversationHistoryCreate


class ConversationHistoryService:
    def __init__(self, db: AsyncSession):
        """
        Why: 대화 히스토리 작업에 사용할 DB 세션을 주입합니다.

        Args:
            db: 비동기 SQLAlchemy 세션.
        """
        self.db = db

    async def add(
        self, conv_id: int, data: ConversationHistoryCreate
    ) -> ConversationHistory:
        """
        Summary: 대화 히스토리를 추가합니다.

        Args:
            conv_id: 대화 ID.
            data: 히스토리 생성 데이터.

        Returns:
            ConversationHistory: 생성된 히스토리 엔티티.

        Side Effects:
            - DB 레코드 생성
        """
        hist = ConversationHistory(
            conversation_id=conv_id, sender=data.sender, content=data.content
        )
        self.db.add(hist)
        await self.db.commit()
        await self.db.refresh(hist)
        return hist

    async def list(self, conv_id: int) -> list[ConversationHistory]:
        """
        Summary: 대화 히스토리를 시간순으로 조회합니다.

        Args:
            conv_id: 대화 ID.

        Returns:
            list[ConversationHistory]: 히스토리 목록.

        Side Effects:
            - DB 조회
        """
        result = await self.db.execute(
            select(ConversationHistory)
            .where(ConversationHistory.conversation_id == conv_id)
            .order_by(ConversationHistory.timestamp)
        )
        return result.scalars().all()
