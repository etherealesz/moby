from fastapi import APIRouter

from modules.waste_categories.routers.category.router import router as category_router

router = APIRouter()
router.include_router(category_router)
