from pydantic import BaseModel


class DFileMeta(BaseModel):
    filename: str | None
    content_type: str | None
    content: bytes
