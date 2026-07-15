from typing import Dict, List

from fastapi import HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.exceptions.common import (
    InternalServerError,
    InvalidJSONFormatError,
    MethodNotAllowedError,
    RequestBodyRequiredError,
    ResourceNotFoundError,
    UnsupportedMediaTypeError,
    ValidationError,
)
from app.utils.standard_response_builder import StandardResponseBuilder
from core.exceptions.bulk_operation import BulkOperationError

ERROR_TYPE_CODE: Dict[str, str] = {
    "missing": "REQUIRED",
}


async def starlette_http_exception_handler(request: Request, exc: Exception):
    if not isinstance(exc, StarletteHTTPException):
        raise exc

    if exc.status_code == status.HTTP_404_NOT_FOUND:
        status_code = status.HTTP_404_NOT_FOUND
        response = (
            StandardResponseBuilder()
            .set_status_code(status_code)
            .set_error(ResourceNotFoundError())
            .build()
        )
        return JSONResponse(status_code=status_code, content=jsonable_encoder(response))

    if exc.status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
        status_code = status.HTTP_405_METHOD_NOT_ALLOWED
        response = (
            StandardResponseBuilder()
            .set_status_code(status_code)
            .set_error(MethodNotAllowedError())
            .build()
        )
        return JSONResponse(status_code=status_code, content=jsonable_encoder(response))

    if exc.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE:
        status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
        response = (
            StandardResponseBuilder()
            .set_status_code(status_code)
            .set_error(UnsupportedMediaTypeError())
            .build()
        )
        return JSONResponse(status_code=status_code, content=jsonable_encoder(response))

    raise exc


async def bulk_operation_error_handler(request: Request, exc: Exception):
    if not isinstance(exc, BulkOperationError):
        raise exc

    status_code = status.HTTP_207_MULTI_STATUS
    response = StandardResponseBuilder().from_bulk_operation_error(exc).build()
    return JSONResponse(status_code=status_code, content=jsonable_encoder(response))


async def http_exception_handler(request: Request, exc: Exception):
    if not isinstance(exc, HTTPException):
        raise exc

    response = StandardResponseBuilder().from_http_exception(exc).build()
    return JSONResponse(status_code=exc.status_code, content=jsonable_encoder(response))


async def validation_error_handler(request: Request, exc: Exception):
    if not isinstance(exc, RequestValidationError):
        raise exc

    if len(exc.errors()) == 1:
        # Check if the error is due to missing request body (e.g., when the endpoint expects a JSON body but none is provided)
        if "body" in exc.errors()[0]["loc"] and not exc.body:
            status_code = status.HTTP_400_BAD_REQUEST
            response = (
                StandardResponseBuilder()
                .set_status_code(status_code)
                .set_error(RequestBodyRequiredError())
                .build()
            )
            return JSONResponse(
                status_code=status_code,
                content=jsonable_encoder(response),
            )

        # Check if the error is due to invalid JSON format in the request body
        if exc.errors()[0]["type"] == "json_invalid":
            status_code = status.HTTP_400_BAD_REQUEST
            response = (
                StandardResponseBuilder()
                .set_status_code(status_code)
                .set_error(InvalidJSONFormatError())
                .build()
            )
            return JSONResponse(
                status_code=status_code,
                content=jsonable_encoder(response),
            )

    validation_errors: Dict[str, str] = {}
    value_error_prefix = "Value error, "
    for error in exc.errors():
        # Extract the field name from the error location, field name possibly contains
        # nested fields, e.g., "patient, name, ..."
        nested_field_name: List[str] = [
            str(error_location_part) for error_location_part in error["loc"]
        ][1:]
        field_name: str = ".".join(nested_field_name)

        if error["type"] in ERROR_TYPE_CODE:
            validation_errors[field_name] = (
                f"{field_name.upper()}_{ERROR_TYPE_CODE[error['type']]}"
            )
        else:
            validation_errors[field_name] = str(
                error["msg"].removeprefix(value_error_prefix),
            )

    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    response = (
        StandardResponseBuilder()
        .from_validation_error(ValidationError(validation_errors=validation_errors))
        .build()
    )
    return JSONResponse(status_code=status_code, content=jsonable_encoder(response))


async def uncaught_exception_handler(request: Request, exc: Exception):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    response = (
        StandardResponseBuilder()
        .set_status_code(status_code)
        .set_error(InternalServerError())
        .build()
    )
    return JSONResponse(status_code=status_code, content=jsonable_encoder(response))
