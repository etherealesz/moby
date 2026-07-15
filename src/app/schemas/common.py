from pydantic import BaseModel
from pydantic.fields import Field


class SPagination(BaseModel):
    """
    Pagination mixin for paginated data.
    """

    total_pages: int | None = Field(default=None)
    total_items: int | None = Field(default=None)
    per_page_size: int | None = Field(default=None)


class SBulkOperationResult(BaseModel):
    """
    Result mixin for bulk operations.
    """

    total_count: int | None = Field(default=None)
    success_count: int | None = Field(default=None)
    failure_count: int | None = Field(default=None)
