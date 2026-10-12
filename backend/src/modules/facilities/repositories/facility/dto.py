from pydantic import BaseModel, Field

from core.dtos.pagination import DPagination
from core.enums.waste_category import EWasteCategory


class DGetAllFacilities(BaseModel):
    category: EWasteCategory | None = Field(default=None)
    city: str | None = Field(default=None)
    search: str | None = Field(default=None)
    pagination: DPagination | None = Field(default=None)
