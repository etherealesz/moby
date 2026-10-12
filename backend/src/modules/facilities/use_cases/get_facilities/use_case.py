from injector import inject

from core.constants.pagination import DEFAULT_PAGINATION_SIZE
from core.dtos.pagination import DPaginatedResults
from core.logger.factory import create_app_logger
from modules.facilities.models.facility import Facility
from modules.facilities.repositories.facility.dto import DGetAllFacilities
from modules.facilities.repositories.facility.protocol import FacilityRepository
from modules.facilities.use_cases.get_facilities.dto import DGetFacilities

logger = create_app_logger()


class GetFacilitiesUseCase:
    @inject
    def __init__(self, facility_repository: FacilityRepository) -> None:
        self._facility_repository = facility_repository

    async def execute(self, dto: DGetFacilities) -> DPaginatedResults[Facility]:
        logger.info("Executing GetFacilitiesUseCase")

        repo_dto = DGetAllFacilities(
            category=dto.category,
            city=dto.city,
            search=dto.query,
            pagination=dto.pagination,
        )
        facilities = await self._facility_repository.get_all(repo_dto)

        return DPaginatedResults(
            total_items=facilities.total_items,
            current_page=dto.pagination.page if dto.pagination else 1,
            items_per_page=(
                dto.pagination.items_per_page
                if dto.pagination
                else DEFAULT_PAGINATION_SIZE
            ),
            results=facilities.results,
        )
