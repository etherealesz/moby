from typing import Protocol, runtime_checkable

from core.enums.network_type import ENetworkType
from modules.navigation.repositories.road_graph.dto import DBoundingBox, DRoadEdgeRow


@runtime_checkable
class RoadGraphRepository(Protocol):
    async def get_edges_in_bbox(
        self,
        network_type: ENetworkType,
        bbox: DBoundingBox,
    ) -> list[DRoadEdgeRow]: ...
