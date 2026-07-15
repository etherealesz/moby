from fastapi import APIRouter

from core.constants.url import (
    BASE_API_URL_PREFIX,
    BASE_URL_PREFIX,
    BASE_WEBHOOK_URL_PREFIX,
    BASE_WEBSOCKET_URL_PREFIX,
)
from modules.etc.router import router as etc_router
from modules.posts.router import router as post_api_router
from modules.navigation.router import router as navigation_api_router


def create_api_router() -> APIRouter:
    """
    Create and return the API router for the application.

    Returns:
        APIRouter: The API router instance with all included routes.
    """

    api_router = APIRouter(prefix=BASE_API_URL_PREFIX)
    api_router.include_router(post_api_router)
    api_router.include_router(navigation_api_router)
    return api_router


def create_websocket_router() -> APIRouter:
    """
    Create and return the WebSocket router for the application.

    Returns:
        APIRouter: The WebSocket router instance with all included routes.
    """

    websocket_router = APIRouter(prefix=BASE_WEBSOCKET_URL_PREFIX)
    return websocket_router


def create_webhook_router() -> APIRouter:
    """
    Create and return the Webhook router for the application.

    Returns:
        APIRouter: The Webhook router instance with all included routes.
    """

    webhook_router = APIRouter(prefix=BASE_WEBHOOK_URL_PREFIX)
    return webhook_router


def create_root_router() -> APIRouter:
    """
    Create and return the root router for the application.

    Returns:
        APIRouter: The root router instance with all included routes.
    """

    root_router = APIRouter(prefix=BASE_URL_PREFIX)
    root_router.include_router(etc_router)
    return root_router
