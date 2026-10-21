from injector import inject

from core.logger.factory import create_app_logger
from modules.navigation.services.navigation_service.dto import DRouteResult
from modules.navigation.services.navigation_service.service import NavigationService
from modules.navigation.use_cases.find_route.dto import DFindRoute

logger = create_app_logger()


class FindRouteUseCase:
    @inject
    def __init__(self, navigation_service: NavigationService) -> None:
        self._navigation_service = navigation_service

    async def execute(self, dto: DFindRoute) -> DRouteResult:
        logger.info("Executing FindRouteUseCase")

        return await self._navigation_service.find_route(
            user_lat=dto.latitude,
            user_lon=dto.longitude,
            category=dto.category,
            network_type=dto.network_type,
            facility_id=dto.facility_id,
        )
