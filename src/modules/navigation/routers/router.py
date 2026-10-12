from fastapi import APIRouter

from modules.navigation.routers.route.router import router as route_router

router = APIRouter()
router.include_router(route_router)
