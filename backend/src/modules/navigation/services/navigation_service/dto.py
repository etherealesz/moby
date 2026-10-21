from pydantic import BaseModel

from core.enums.network_type import ENetworkType
from modules.facilities.models.facility import Facility


class DSearchResult(BaseModel):
    path: list[int]
    distance_meter: float
    explored_nodes: int
    computation_time_ms: float


class DCandidateRoute(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    facility: Facility
    straight_distance_meter: float
    route_distance_meter: float | None
    explored_nodes: int
    computation_time_ms: float


class DRouteResult(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    facility: Facility
    network_type: ENetworkType
    route: list[tuple[float, float]]
    distance_meter: float
    explored_nodes: int
    computation_time_ms: float
    graph_load_time_ms: float
    graph_node_count: int
    graph_edge_count: int
    candidates: list[DCandidateRoute]
