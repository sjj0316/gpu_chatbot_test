from pydantic import BaseModel
from datetime import datetime


class ConversationHistoryCreate(BaseModel):
    sender: str
    content: str


class ConversationHistoryRead(BaseModel):
    id: int
    conversation_id: int
    sender: str
    content: str
    timestamp: datetime

    class Config:
        from_attributes = True
