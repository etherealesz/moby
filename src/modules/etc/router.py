from typing import List
from fastapi import APIRouter, status

from app.schemas.response import SStandardResponse
from app.utils.standard_response_builder import StandardResponseBuilder

tags: List = ["API / Etc"]
router = APIRouter(tags=tags)


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> SStandardResponse:
    return StandardResponseBuilder().build()
