from injector import inject
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from core.dtos.pagination import DResultsWithTotalItems
from core.enums.waste_category import EWasteCategory
from core.logger.factory import create_app_logger
from infrastructures.databases.master import DatabaseMasterSession
from infrastructures.databases.utils.pagination_helper import build_limit_offset
from modules.facilities.exceptions.facility import GetFacilityFailedError
from modules.facilities.models.facility import Facility
from modules.facilities.repositories.facility.dto import DGetAllFacilities
from modules.facilities.repositories.facility.utils import (
    build_accepts_category_clause,
    build_get_all_search_clause,
)

logger = create_app_logger()


class IFacilityRepository:
    @inject
    def __init__(self, session: DatabaseMasterSession) -> None:
        self._session = session

    async def get_all(
        self,
        dto: DGetAllFacilities | None,
    ) -> DResultsWithTotalItems[Facility]:
        logger.info("Executing get_all method in IFacilityRepository")

        stmt = select(Facility).order_by(Facility.facility_id.asc())
        if dto and dto.category:
            stmt = stmt.where(build_accepts_category_clause(dto.category))
        if dto and dto.city:
            stmt = stmt.where(Facility.city.ilike(dto.city))
        if dto and dto.search:
            stmt = stmt.where(build_get_all_search_clause(dto.search))

        total = select(func.count(1)).select_from(stmt.subquery())
        if dto and dto.pagination:
            limit, offset = build_limit_offset(dto.pagination)
            stmt = stmt.offset(offset).limit(limit)
        stmt = stmt.options(selectinload(Facility.categories))

        try:
            total_res = await self._session.execute(total)
            res = await self._session.execute(stmt)
        except Exception as exc:
            logger.exception("Error occurred while fetching facilities", exc_info=True)
            raise GetFacilityFailedError from exc

        return DResultsWithTotalItems(
            total_items=total_res.scalar_one(),
            results=list(res.scalars().all()),
        )

    async def get_by_category(self, category: EWasteCategory) -> list[Facility]:
        logger.info("Executing get_by_category method in IFacilityRepository")

        stmt = (
            select(Facility)
            .where(build_accepts_category_clause(category))
            .order_by(Facility.facility_id.asc())
        )

        try:
            res = await self._session.execute(stmt)
        except Exception as exc:
            logger.exception(
                "Error occurred while fetching facilities by category", exc_info=True
            )
            raise GetFacilityFailedError from exc

        return list(res.scalars().all())
