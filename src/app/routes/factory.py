from fastapi import APIRouter

from core.constants.url import (
    BASE_API_URL_PREFIX,
    BASE_URL_PREFIX,
    BASE_WEBHOOK_URL_PREFIX,
    BASE_WEBSOCKET_URL_PREFIX,
)
from modules.classification.routers.router import router as classification_router
from modules.classification.routers.router import (
    websocket_router as classification_websocket_router,
)
from modules.etc.routers.health.router import router as etc_health_router
from modules.facilities.routers.router import router as facility_router
from modules.info.routers.router import router as info_router
from modules.navigation.routers.router import router as navigation_router
from modules.waste_categories.routers.router import router as waste_category_router


def create_api_router() -> APIRouter:
    api_router = APIRouter(prefix=BASE_API_URL_PREFIX)
    api_router.include_router(classification_router)
    api_router.include_router(navigation_router)
    api_router.include_router(waste_category_router)
    api_router.include_router(facility_router)
    api_router.include_router(info_router)
    return api_router


def create_websocket_router() -> APIRouter:
    websocket_router = APIRouter(prefix=BASE_WEBSOCKET_URL_PREFIX)
    websocket_router.include_router(classification_websocket_router)
    return websocket_router


def create_webhook_router() -> APIRouter:
    webhook_router = APIRouter(prefix=BASE_WEBHOOK_URL_PREFIX)
    return webhook_router


def create_root_router() -> APIRouter:
    root_router = APIRouter(prefix=BASE_URL_PREFIX)
    root_router.include_router(etc_health_router)
    return root_router
