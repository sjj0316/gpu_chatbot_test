from datetime import datetime
from pydantic import BaseModel, ConfigDict


class WikiPageRead(BaseModel):
    slug: str
    title: str
    content: str
    updated_at: datetime | None = None
    updated_by: str | None = None

    model_config = ConfigDict(from_attributes=True)


class WikiPageUpdate(BaseModel):
    title: str | None = None
    content: str
