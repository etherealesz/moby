from typing import Protocol, runtime_checkable

from core.dtos.pagination import DResultsWithTotalItems
from core.enums.waste_category import EWasteCategory
from modules.facilities.models.facility import Facility
from modules.facilities.repositories.facility.dto import DGetAllFacilities


@runtime_checkable
class FacilityRepository(Protocol):
    async def get_all(
        self,
        dto: DGetAllFacilities | None,
    ) -> DResultsWithTotalItems[Facility]: ...

    async def get_by_category(self, category: EWasteCategory) -> list[Facility]: ...
