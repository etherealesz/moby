from typing import Protocol, runtime_checkable

from modules.waste_categories.models.waste_category import WasteCategory


@runtime_checkable
class WasteCategoryRepository(Protocol):
    async def get_all_with_subcategories(self) -> list[WasteCategory]: ...
