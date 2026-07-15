from typing import Dict, Generic, Sequence

from pydantic import BaseModel, Field
from typing_extensions import TypeVar

from app.schemas.common import SBulkOperationResult, SPagination

T = TypeVar("T", bound=BaseModel)


class SStandardErrorResponse(BaseModel):
    """
    A standard error response model for conveying error information.
    """

    status: bool = Field(default=False)
    message: str = Field(default="")
    detail: Dict[str, str] | None = Field(default=None)
    code: int = Field(default=0)


class _SBaseStandardResponse(BaseModel, Generic[T]):
    """
    A base standard response model for metadata and error information.
    """

    error: SStandardErrorResponse = Field(default=SStandardErrorResponse())


class SStandardResponse(_SBaseStandardResponse, Generic[T]):
    """
    A standard response model for returning a single item with metadata and links.
    """

    meta: None = Field(default=None)
    data: T | None = Field(default=None)


class SStandardListResponse(_SBaseStandardResponse, Generic[T]):
    """
    A standard response model for returning a list of items with metadata and links.
    """

    meta: None = Field(default=None)
    data: Sequence[T] = Field(default_factory=list)


class SStandardPaginatedListResponse(_SBaseStandardResponse, Generic[T]):
    """
    A standard response model for returning a paginated list of items with
    metadata and links.
    """

    meta: SPagination
    data: Sequence[T] = Field(default_factory=list)


class SStandardBulkOperationResultResponse(_SBaseStandardResponse, Generic[T]):
    """
    A standard response model for returning the result of a bulk operation with
    metadata and links.
    """

    meta: SBulkOperationResult
    data: Sequence[T] = Field(default_factory=list)
