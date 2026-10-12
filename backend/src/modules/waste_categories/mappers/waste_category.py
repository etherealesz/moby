from modules.waste_categories.models.waste_category import WasteCategory
from modules.waste_categories.models.waste_subcategory import WasteSubcategory
from modules.waste_categories.schemas.waste_category import (
    SWasteCategoryResponse,
    SWasteSubcategoryResponse,
)


def map_waste_subcategory_to_response(
    subcategory: WasteSubcategory,
) -> SWasteSubcategoryResponse:
    return SWasteSubcategoryResponse(
        subcategory_id=subcategory.subcategory_id,
        subcategory_name=subcategory.subcategory_name,
        description=subcategory.description,
    )


def map_waste_category_to_response(category: WasteCategory) -> SWasteCategoryResponse:
    return SWasteCategoryResponse(
        category_id=category.category_id,
        category_name=category.category_name,
        category_code=category.category_code,
        description=category.description,
        subcategories=[
            map_waste_subcategory_to_response(subcategory)
            for subcategory in category.subcategories
        ],
    )
