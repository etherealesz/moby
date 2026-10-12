from fastapi import APIRouter

from modules.classification.routers.classify.router import router as classify_router
from modules.classification.routers.classify.websocket import (
    router as classify_websocket_router,
)

router = APIRouter()
router.include_router(classify_router)

websocket_router = APIRouter()
websocket_router.include_router(classify_websocket_router)
