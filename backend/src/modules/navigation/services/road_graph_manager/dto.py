from typing import NamedTuple


class DNearestNode(NamedTuple):
    node_id: int
    distance_meter: float


class DNeighbor(NamedTuple):
    node_id: int
    distance_meter: float
