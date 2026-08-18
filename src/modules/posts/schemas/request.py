from pydantic import BaseModel, field_validator


class SPostPostsRequest(BaseModel):
    title: str
    content: str

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        TITLE_MAX_LENGTH = 100
        TITLE_MIN_LENGTH = 5

        if not (TITLE_MIN_LENGTH <= len(value) <= TITLE_MAX_LENGTH):
            raise ValueError(
                f"Title must be between {TITLE_MIN_LENGTH} and {TITLE_MAX_LENGTH} characters long."
            )

        return value.strip()

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        CONTENT_MAX_LENGTH = 1000
        CONTENT_MIN_LENGTH = 10

        if not (CONTENT_MIN_LENGTH <= len(value) <= CONTENT_MAX_LENGTH):
            raise ValueError(
                f"Content must be between {CONTENT_MIN_LENGTH} and {CONTENT_MAX_LENGTH} characters long."
            )

        return value.strip()
