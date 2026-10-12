from pydantic import BaseModel, Field

from core.constants.pagination import DEFAULT_PAGINATION_SIZE


class SOptionalPagination(BaseModel):
    page: int | None = Field(default=None)
    page_size: int | None = Field(default=None)


class SPagination(BaseModel):
    page: int = Field(default=1, gt=0)
    page_size: int = Field(default=DEFAULT_PAGINATION_SIZE, gt=0)
