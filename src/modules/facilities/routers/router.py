from fastapi import APIRouter

from modules.facilities.routers.facility.router import router as facility_router

router = APIRouter()
router.include_router(facility_router)
