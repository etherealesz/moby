from fastapi import APIRouter, HTTPException, status
from fastapi_injector import Injected

from app.schemas.predefined import SGenericErrorResponse, SStandardValidationErrorResponse
from app.schemas.response import SStandardResponse
from app.utils.standard_response_builder import StandardResponseBuilder
from modules.facilities.exceptions.facility import GetFacilityFailedError
from modules.navigation.exceptions.navigation import (
    FacilityNotFoundError,
    FacilityOutOfRangeError,
    GetRoadGraphFailedError,
    LocationOutOfCoverageError,
    RoadGraphNotAvailableError,
    RouteNotFoundError,
)
from modules.navigation.mappers.route import map_route_result_to_response
from modules.navigation.routers.route.request import SRouteRequest
from modules.navigation.schemas.route import SRouteResponse
from modules.navigation.use_cases.find_route.dto import DFindRoute
from modules.navigation.use_cases.find_route.use_case import FindRouteUseCase

tags: list = ["API / Navigation"]
router = APIRouter(prefix="/route", tags=tags)


@router.post(
    path="",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": SGenericErrorResponse},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": SStandardValidationErrorResponse
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": SGenericErrorResponse},
    },
)
async def find_route(
    request: SRouteRequest,
    find_route_use_case=Injected(FindRouteUseCase),
) -> SStandardResponse[SRouteResponse]:
    dto = DFindRoute(
        latitude=request.latitude,
        longitude=request.longitude,
        category=request.category,
        network_type=request.network_type,
        facility_id=request.facility_id,
    )

    try:
        result = await find_route_use_case.execute(dto)
    except (
        FacilityNotFoundError,
        FacilityOutOfRangeError,
        LocationOutOfCoverageError,
        RoadGraphNotAvailableError,
        RouteNotFoundError,
    ) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except (GetFacilityFailedError, GetRoadGraphFailedError) as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )

    response_data = map_route_result_to_response(result)
    return (
        StandardResponseBuilder()
        .set_status_code(status.HTTP_200_OK)
        .set_data(response_data)
        .build()
    )
