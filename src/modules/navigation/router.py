from fastapi import APIRouter, HTTPException, status
from fastapi_injector import Injected
from modules.navigation.use_cases.find_route import FindRouteUseCase
from modules.navigation.schemas import SRouteRequest, SNavigationResponse
from app.schemas.response import SStandardResponse
from app.utils.standard_response_builder import StandardResponseBuilder

tags = ["API / Navigation"]
router = APIRouter(prefix="/navigation", tags=tags)

@router.post("/route", status_code=status.HTTP_200_OK)
async def get_route(
    body: SRouteRequest,
    find_route_use_case: FindRouteUseCase = Injected(FindRouteUseCase)
) -> SStandardResponse[SNavigationResponse]:
    """
    Endpoint untuk mencari rute terpendek menggunakan algoritma A* Search kustom
    berdasarkan peta nyata OpenStreetMap (OSMnx).
    """
    try:
        result = await find_route_use_case.execute(
            start_lat=body.start_lat,
            start_lon=body.start_lon,
            end_lat=body.end_lat,
            end_lon=body.end_lon,
            mode=body.mode
        )
        response_data = SNavigationResponse(**result)
        return StandardResponseBuilder().set_data(response_data).build()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc)
        )

