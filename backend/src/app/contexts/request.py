from contextvars import ContextVar
from datetime import datetime

from pydantic import BaseModel


class RequestContext(BaseModel):
    request_id: str
    timestamp: datetime
    ip: str | None
    path: str
    method: str


request_context: ContextVar[RequestContext | None] = ContextVar(
    "request_context",
    default=None,
)
