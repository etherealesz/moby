from injector import inject

from core.logger.factory import create_app_logger
from modules.waste_categories.models.waste_category import WasteCategory
from modules.waste_categories.repositories.waste_category.protocol import (
    WasteCategoryRepository,
)

logger = create_app_logger()


class GetCategoriesUseCase:
    @inject
    def __init__(self, waste_category_repository: WasteCategoryRepository) -> None:
        self._waste_category_repository = waste_category_repository

    async def execute(self) -> list[WasteCategory]:
        logger.info("Executing GetCategoriesUseCase")

        return await self._waste_category_repository.get_all_with_subcategories()
