from injector import inject
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from core.logger.factory import create_app_logger
from infrastructures.databases.master import DatabaseMasterSession
from modules.waste_categories.exceptions.waste_category import (
    GetWasteCategoryFailedError,
)
from modules.waste_categories.models.waste_category import WasteCategory

logger = create_app_logger()


class IWasteCategoryRepository:
    @inject
    def __init__(self, session: DatabaseMasterSession) -> None:
        self._session = session

    async def get_all_with_subcategories(self) -> list[WasteCategory]:
        logger.info(
            "Executing get_all_with_subcategories method in IWasteCategoryRepository"
        )

        stmt = (
            select(WasteCategory)
            .options(selectinload(WasteCategory.subcategories))
            .order_by(WasteCategory.category_id.asc())
        )

        try:
            res = await self._session.execute(stmt)
        except Exception as exc:
            logger.exception(
                "Error occurred while fetching waste categories", exc_info=True
            )
            raise GetWasteCategoryFailedError from exc

        return list(res.scalars().all())
