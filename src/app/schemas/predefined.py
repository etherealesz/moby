from fastapi import status
from pydantic import Field

from app.schemas.response import SStandardErrorResponse, SStandardResponse


class SGenericErrorResponse(SStandardResponse):
    error: SStandardErrorResponse = Field(
        default=SStandardErrorResponse(
            status=True,
            code=999,
            message="ERROR_CODE",
        )
    )


class SStandardValidationErrorResponse(SStandardResponse):
    error: SStandardErrorResponse = Field(
        default=SStandardErrorResponse(
            status=True,
            code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            message="VALIDATION_ERROR",
            detail={},
        )
    )


class SStandardBulkOperationErrorResponse(SStandardResponse):
    error: SStandardErrorResponse = Field(
        default=SStandardErrorResponse(
            status=True,
            code=status.HTTP_207_MULTI_STATUS,
            message="BULK_OPERATION_ERROR",
            detail={},
        )
    )


class SStandardInternalServerErrorResponse(SStandardResponse):
    error: SStandardErrorResponse = Field(
        default=SStandardErrorResponse(
            status=True,
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="INTERNAL_SERVER_ERROR",
        )
    )
