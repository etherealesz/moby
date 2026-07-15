from typing import Any, Dict, Generic, Sequence, TypeVar

from fastapi import HTTPException, status
from pydantic import BaseModel, Field

from app.exceptions.common import ValidationError
from app.schemas.common import SBulkOperationResult, SPagination
from app.schemas.response import (
    SStandardBulkOperationResultResponse,
    SStandardErrorResponse,
    SStandardListResponse,
    SStandardPaginatedListResponse,
    SStandardResponse,
)
from core.dtos.bulk_operation import DBulkOperationResultMeta
from core.dtos.pagination import DPaginationMeta
from core.exceptions.bulk_operation import BulkOperationError

T = TypeVar("T", bound=BaseModel)


class ResponseMetaVariables(BaseModel):
    """
    Helper class to hold meta variables for building responses.
    """

    pagination_meta: DPaginationMeta | None = Field(default=None)
    bulk_operation_result_meta: DBulkOperationResultMeta | None = Field(default=None)


class StandardResponseBuilder(Generic[T]):
    """
    Builder class for constructing standardized API responses.
    """

    def __init__(self) -> None:
        self._status_code: int = status.HTTP_200_OK
        self._error: Exception | None = None
        self._error_detail: Dict[str, str] | None = None
        self._data: T | Sequence[T] | None = None
        self._meta_variables: ResponseMetaVariables = ResponseMetaVariables()

    def set_status_code(
        self,
        status_code: int = status.HTTP_200_OK,
    ) -> "StandardResponseBuilder[T]":
        self._status_code = status_code
        return self

    def set_error(self, error: Exception | None) -> "StandardResponseBuilder[T]":
        self._error = error
        return self

    def from_http_exception(
        self,
        http_exception: HTTPException,
    ) -> "StandardResponseBuilder[T]":
        self._error = Exception(http_exception.detail)
        self._status_code = http_exception.status_code
        return self

    def from_bulk_operation_error(
        self,
        error: BulkOperationError,
    ) -> "StandardResponseBuilder[T]":
        self._error = error
        self._data = error.bulk_operation_result_schema
        self._meta_variables.bulk_operation_result_meta = error.bulk_operation_result_meta
        self._error_detail = {
            name: errors[0]
            for name, errors in error.bulk_operation_result_meta.errors.items()
            if len(errors) > 0
        }
        self._status_code = status.HTTP_207_MULTI_STATUS
        return self

    def from_validation_error(
        self,
        validation_error: ValidationError,
    ) -> "StandardResponseBuilder[T]":
        self._error = validation_error
        self._error_detail = validation_error.validation_errors
        self._status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        return self

    def set_data(self, data: T | Sequence[T] | None) -> "StandardResponseBuilder[T]":
        self._data = data
        return self

    def set_pagination_meta(self, meta: DPaginationMeta) -> "StandardResponseBuilder[T]":
        self._meta_variables.pagination_meta = meta
        return self

    def set_bulk_operation_result_meta(
        self,
        meta: DBulkOperationResultMeta,
    ) -> "StandardResponseBuilder[T]":
        self._meta_variables.bulk_operation_result_meta = meta
        return self

    def _build_meta_response(self) -> Any:
        if self._meta_variables.pagination_meta:
            return SPagination(
                total_items=self._meta_variables.pagination_meta.total_items,
                total_pages=self._meta_variables.pagination_meta.total_pages,
                per_page_size=self._meta_variables.pagination_meta.items_per_page,
            )

        if self._meta_variables.bulk_operation_result_meta:
            return SBulkOperationResult(
                total_count=self._meta_variables.bulk_operation_result_meta.total_count,
                success_count=self._meta_variables.bulk_operation_result_meta.success_count,
                failure_count=self._meta_variables.bulk_operation_result_meta.failure_count,
            )

        return None

    def _build_bulk_operation_error_response(self):
        assert self._error, "Error must be set to build a bulk operation error response"
        assert self._data and isinstance(self._data, Sequence), (
            "Data must be a collection for bulk operation error responses"
        )
        assert self._meta_variables.bulk_operation_result_meta, (
            "Bulk operation result meta must be set to build a bulk operation error response"
        )

        meta = self._build_meta_response()
        error = SStandardErrorResponse(
            status=True,
            message=str(self._error),
            detail=self._error_detail,
            code=self._status_code,
        )
        return SStandardBulkOperationResultResponse[T](
            meta=meta,
            error=error,
            data=self._data,
        )

    def _build_error_response(self):
        assert self._error, "Error must be set to build an error response"

        if isinstance(self._error, BulkOperationError):
            return self._build_bulk_operation_error_response()

        error = SStandardErrorResponse(
            status=True,
            message=str(self._error),
            detail=self._error_detail,
            code=self._status_code,
        )
        return SStandardResponse[T](data=None, error=error)

    def _build_paginated_list_response(self):
        assert self._meta_variables.pagination_meta, (
            "Pagination meta must be set to build a paginated list response"
        )
        assert isinstance(self._data, Sequence), (
            "Data must be a collection for paginated list responses"
        )

        meta = self._build_meta_response()
        error = SStandardErrorResponse(
            status=False,
            message="",
            code=self._status_code,
        )
        return SStandardPaginatedListResponse(meta=meta, error=error, data=self._data)

    def _build_bulk_operation_result_response(self):
        assert self._meta_variables.bulk_operation_result_meta, (
            "Bulk operation result meta must be set to build a bulk operation result response"
        )
        assert isinstance(self._data, Sequence), (
            "Data must be a collection for bulk operation result responses"
        )

        meta = self._build_meta_response()
        error = SStandardErrorResponse(
            status=False,
            message="",
            code=self._status_code,
        )
        return SStandardBulkOperationResultResponse(
            meta=meta,
            error=error,
            data=self._data,
        )

    def _build_list_response(self):
        assert isinstance(self._data, Sequence), (
            "Data must be a collection for sequence responses"
        )

        if self._meta_variables.pagination_meta:
            return self._build_paginated_list_response()
        if self._meta_variables.bulk_operation_result_meta:
            return self._build_bulk_operation_result_response()

        meta = self._build_meta_response()
        error = SStandardErrorResponse(
            status=False,
            message="",
            code=self._status_code,
        )
        return SStandardListResponse(meta=meta, error=error, data=self._data)

    def _build_single_response(self):
        assert not isinstance(self._data, Sequence), (
            "Data must not be a collection for single response"
        )

        meta = self._build_meta_response()
        error = SStandardErrorResponse(
            status=False,
            message="",
            code=self._status_code,
        )
        return SStandardResponse(meta=meta, error=error, data=self._data)

    def build(self) -> Any:
        if self._error:
            return self._build_error_response()

        if isinstance(self._data, Sequence):
            return self._build_list_response()
        return self._build_single_response()
