from pydantic import Field

from app.schemas.request import SPagination
from core.enums.waste_category import EWasteCategory


class SGetFacilitiesQueryParams(SPagination):
    category: EWasteCategory | None = Field(default=None)
    city: str | None = Field(default=None)
    query: str | None = Field(default=None)
