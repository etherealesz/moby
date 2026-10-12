from typing import Any
from core.dtos.bulk_operation import DBulkOperationResultMeta


class BulkOperationError(Exception):
    def __init__(
        self,
        bulk_operation_result_meta: DBulkOperationResultMeta,
        bulk_operation_result_schema: Any,
    ):
        self._bulk_operation_result_meta = bulk_operation_result_meta
        self._bulk_operation_result_schema = bulk_operation_result_schema

        super().__init__("BULK_OPERATION_ERROR")

    @property
    def bulk_operation_result_meta(self) -> DBulkOperationResultMeta:
        return self._bulk_operation_result_meta

    @property
    def bulk_operation_result_schema(self) -> Any:
        return self._bulk_operation_result_schema
