from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status
from fastapi_injector import Injected

from app.mappers.pagination import map_pagination_schema_to_pagination_dto
from app.schemas.predefined import SGenericErrorResponse, SStandardValidationErrorResponse
from app.schemas.response import SStandardPaginatedListResponse
from app.utils.standard_response_builder import StandardResponseBuilder
from modules.facilities.exceptions.facility import GetFacilityFailedError
from modules.facilities.mappers.facility import map_facility_to_response
from modules.facilities.routers.facility.request import SGetFacilitiesQueryParams
from modules.facilities.schemas.facility import SFacilityResponse
from modules.facilities.use_cases.get_facilities.dto import DGetFacilities
from modules.facilities.use_cases.get_facilities.use_case import GetFacilitiesUseCase

tags: list = ["API / Facilities"]
router = APIRouter(prefix="/facilities", tags=tags)


@router.get(
    path="",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": SStandardValidationErrorResponse
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": SGenericErrorResponse},
    },
)
async def get_facilities(
    params: Annotated[SGetFacilitiesQueryParams, Query()],
    get_facilities_use_case=Injected(GetFacilitiesUseCase),
) -> SStandardPaginatedListResponse[SFacilityResponse]:
    pagination = map_pagination_schema_to_pagination_dto(params)
    dto = DGetFacilities(
        category=params.category,
        city=params.city,
        query=params.query,
        pagination=pagination,
    )

    try:
        facilities = await get_facilities_use_case.execute(dto)
    except GetFacilityFailedError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )

    response_data = [
        map_facility_to_response(facility, include_categories=True)
        for facility in facilities.results
    ]
    return (
        StandardResponseBuilder()
        .set_status_code(status.HTTP_200_OK)
        .set_pagination_meta(facilities)
        .set_data(response_data)
        .build()
    )
