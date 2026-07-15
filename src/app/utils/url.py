from fastapi import Request

from core.config.settings import ENVIRONMENT
from core.constants.environment import (
    EXPOSEABLE_API_DOCUMENTATION_APPLICATION_ENVIRONMENTS,
)
from core.constants.url import (
    BASE_API_URL_PREFIX,
    BASE_URL_PREFIX,
    BASE_WEBHOOK_URL_PREFIX,
    BASE_WEBSOCKET_URL_PREFIX,
    LOCAL_DOCS_URL,
    LOCAL_OPENAPI_URL,
    LOCAL_REDOC_URL,
    NON_LOCAL_DOCS_URL,
    NON_LOCAL_OPENAPI_URL,
    NON_LOCAL_REDOC_URL,
)


def get_base_url(request: Request) -> str:
    """
    Get the base URL from the request.

    Args:
        request (Request): The incoming HTTP request.

    Returns:
        str: The base URL of the request.
    """

    return f"{str(request.base_url)}{BASE_URL_PREFIX}"


def get_base_api_url(request: Request) -> str:
    """
    Get the base API URL from the request.

    Args:
        request (Request): The incoming HTTP request.

    Returns:
        str: The base API URL of the request.
    """

    return f"{str(request.base_url)}{BASE_API_URL_PREFIX}"


def get_base_webhook_url(request: Request) -> str:
    """
    Get the base webhook URL from the request.

    Args:
        request (Request): The incoming HTTP request.

    Returns:
        str: The base webhook URL of the request.
    """

    return f"{str(request.base_url)}{BASE_WEBHOOK_URL_PREFIX}"


def get_base_websocket_url(request: Request) -> str:
    """
    Get the base websocket URL from the request.

    Args:
        request (Request): The incoming HTTP request.

    Returns:
        str: The base websocket URL of the request.
    """

    base_url = str(request.base_url)
    if base_url.startswith("http://"):
        base_url = base_url.replace("http://", "ws://")
    elif base_url.startswith("https://"):
        base_url = base_url.replace("https://", "wss://")
    return f"{base_url}{BASE_WEBSOCKET_URL_PREFIX}"


def get_docs_url() -> tuple[str | None, str | None, str | None]:
    """
    Get the URLs for the API documentation (Swagger UI, ReDoc, and OpenAPI JSON).

    Returns:
        tuple[str, str, str]: A tuple containing the URLs for Swagger UI, ReDoc, and OpenAPI JSON.
    """

    if ENVIRONMENT not in EXPOSEABLE_API_DOCUMENTATION_APPLICATION_ENVIRONMENTS:
        return None, None, None

    docs_url = LOCAL_DOCS_URL if ENVIRONMENT == "local" else NON_LOCAL_DOCS_URL
    redoc_url = LOCAL_REDOC_URL if ENVIRONMENT == "local" else NON_LOCAL_REDOC_URL
    openapi_url = LOCAL_OPENAPI_URL if ENVIRONMENT == "local" else NON_LOCAL_OPENAPI_URL
    return docs_url, redoc_url, openapi_url
