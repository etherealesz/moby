from pydantic import BaseModel, Field

from core.enums.network_type import ENetworkType
from core.enums.waste_category import EWasteCategory


class DFindRoute(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    category: EWasteCategory
    network_type: ENetworkType
