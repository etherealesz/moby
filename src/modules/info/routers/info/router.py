from fastapi import APIRouter, status

from app.schemas.response import SStandardResponse
from app.utils.standard_response_builder import StandardResponseBuilder
from modules.info.constants.content import ABOUT_PAGE, HELP_PAGE
from modules.info.schemas.info import SInfoPageResponse

tags: list = ["API / Info"]
router = APIRouter(prefix="/info", tags=tags)


@router.get("/about", status_code=status.HTTP_200_OK)
async def get_about() -> SStandardResponse[SInfoPageResponse]:
    return (
        StandardResponseBuilder()
        .set_status_code(status.HTTP_200_OK)
        .set_data(ABOUT_PAGE)
        .build()
    )


@router.get("/help", status_code=status.HTTP_200_OK)
async def get_help() -> SStandardResponse[SInfoPageResponse]:
    return (
        StandardResponseBuilder()
        .set_status_code(status.HTTP_200_OK)
        .set_data(HELP_PAGE)
        .build()
    )
