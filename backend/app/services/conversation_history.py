from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import ConversationHistory
from app.schemas import ConversationHistoryCreate


class ConversationHistoryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add(
        self, conv_id: int, data: ConversationHistoryCreate
    ) -> ConversationHistory:
        hist = ConversationHistory(
            conversation_id=conv_id, sender=data.sender, content=data.content
        )
        self.db.add(hist)
        await self.db.commit()
        await self.db.refresh(hist)
        return hist

    async def list(self, conv_id: int) -> list[ConversationHistory]:
        result = await self.db.execute(
            select(ConversationHistory)
            .where(ConversationHistory.conversation_id == conv_id)
            .order_by(ConversationHistory.timestamp)
        )
        return result.scalars().all()
