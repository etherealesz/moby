from pydantic import BaseModel


class SInfoSectionResponse(BaseModel):
    title: str
    paragraphs: list[str]


class SInfoPageResponse(BaseModel):
    title: str
    sections: list[SInfoSectionResponse]
