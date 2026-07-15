from pydantic import BaseModel


class DCreatePost(BaseModel):
    title: str
    content: str
