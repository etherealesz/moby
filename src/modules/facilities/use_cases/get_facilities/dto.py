from pydantic import BaseModel

from core.dtos.pagination import DPagination
from core.enums.waste_category import EWasteCategory


class DGetFacilities(BaseModel):
    category: EWasteCategory | None
    city: str | None
    query: str | None
    pagination: DPagination | None
