from datetime import datetime

from pydantic import BaseModel


class SPost(BaseModel):
    id: int
    title: str
    content: str
    uploaded_at: datetime
