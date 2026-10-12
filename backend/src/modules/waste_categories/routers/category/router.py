from fastapi import APIRouter, HTTPException, status
from fastapi_injector import Injected

from app.schemas.predefined import SGenericErrorResponse
from app.schemas.response import SStandardListResponse
from app.utils.standard_response_builder import StandardResponseBuilder
from modules.waste_categories.exceptions.waste_category import (
    GetWasteCategoryFailedError,
)
from modules.waste_categories.mappers.waste_category import (
    map_waste_category_to_response,
)
from modules.waste_categories.schemas.waste_category import SWasteCategoryResponse
from modules.waste_categories.use_cases.get_categories.use_case import (
    GetCategoriesUseCase,
)

tags: list = ["API / Categories"]
router = APIRouter(prefix="/categories", tags=tags)


@router.get(
    path="",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": SGenericErrorResponse},
    },
)
async def get_categories(
    get_categories_use_case=Injected(GetCategoriesUseCase),
) -> SStandardListResponse[SWasteCategoryResponse]:
    try:
        categories = await get_categories_use_case.execute()
    except GetWasteCategoryFailedError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )

    response_data = [map_waste_category_to_response(category) for category in categories]
    return (
        StandardResponseBuilder()
        .set_status_code(status.HTTP_200_OK)
        .set_data(response_data)
        .build()
    )
