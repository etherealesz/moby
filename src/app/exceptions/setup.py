from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.exceptions.handlers import (
    http_exception_handler,
    starlette_http_exception_handler,
    uncaught_exception_handler,
    validation_error_handler,
)


def setup_exception_handlers(app: FastAPI) -> None:
    """
    Setup exception handlers for the FastAPI application.

    Args:
        app (FastAPI): The FastAPI application instance.

    Returns:
        None
    """

    app.add_exception_handler(
        exc_class_or_status_code=StarletteHTTPException,
        handler=starlette_http_exception_handler,
    )

    app.add_exception_handler(
        exc_class_or_status_code=HTTPException,
        handler=http_exception_handler,
    )
    app.add_exception_handler(
        exc_class_or_status_code=RequestValidationError,
        handler=validation_error_handler,
    )

    # Fallback for uncaught exceptions
    app.add_exception_handler(
        exc_class_or_status_code=Exception,
        handler=uncaught_exception_handler,
    )
