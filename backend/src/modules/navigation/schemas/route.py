from pydantic import BaseModel

from core.enums.network_type import ENetworkType
from modules.facilities.schemas.facility import SFacilityResponse


class SCandidateRouteResponse(BaseModel):
    facility: SFacilityResponse
    straight_distance_meter: float
    route_distance_meter: float | None
    explored_nodes: int
    computation_time_ms: float


class SRouteResponse(BaseModel):
    facility: SFacilityResponse
    network_type: ENetworkType
    route: list[tuple[float, float]]
    distance_meter: float
    explored_nodes: int
    computation_time_ms: float
    graph_load_time_ms: float
    graph_node_count: int
    graph_edge_count: int
    candidates: list[SCandidateRouteResponse]
