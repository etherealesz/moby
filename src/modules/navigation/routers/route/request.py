from pydantic import BaseModel, Field

from core.enums.network_type import ENetworkType
from core.enums.waste_category import EWasteCategory


class SRouteRequest(BaseModel):
    latitude: float = Field(ge=-90, le=90, examples=[-6.1754])
    longitude: float = Field(ge=-180, le=180, examples=[106.8272])
    category: EWasteCategory = Field(examples=[EWasteCategory.ANORGANIK])
    network_type: ENetworkType = Field(
        default=ENetworkType.WALK, examples=[ENetworkType.WALK]
    )
