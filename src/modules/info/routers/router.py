from fastapi import APIRouter

from modules.info.routers.info.router import router as info_router

router = APIRouter()
router.include_router(info_router)
