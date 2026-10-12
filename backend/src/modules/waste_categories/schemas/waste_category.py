from pydantic import BaseModel


class SWasteSubcategoryResponse(BaseModel):
    subcategory_id: int
    subcategory_name: str
    description: str | None


class SWasteCategoryResponse(BaseModel):
    category_id: int
    category_name: str
    category_code: str
    description: str | None
    subcategories: list[SWasteSubcategoryResponse]
