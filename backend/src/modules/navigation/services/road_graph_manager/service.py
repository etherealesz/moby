from typing import Iterable

import numpy as np
from injector import inject

from core.enums.network_type import ENetworkType
from core.logger.factory import create_app_logger
from core.utils.geo_helper import haversine_distance, haversine_distances
from modules.navigation.repositories.road_graph.dto import DBoundingBox, DRoadEdgeRow
from modules.navigation.repositories.road_graph.protocol import RoadGraphRepository
from modules.navigation.services.road_graph_manager.dto import DNearestNode, DNeighbor

logger = create_app_logger()


class RoadGraphManager:
    @inject
    def __init__(self, road_graph_repository: RoadGraphRepository) -> None:
        self._road_graph_repository = road_graph_repository
        self._coordinates: dict[int, tuple[float, float]] = {}
        self._adjacency: dict[int, list[DNeighbor]] = {}
        self._edge_count = 0
        self._node_ids = np.empty(0, dtype=np.int64)
        self._latitudes = np.empty(0, dtype=np.float64)
        self._longitudes = np.empty(0, dtype=np.float64)

    @property
    def node_count(self) -> int:
        return len(self._coordinates)

    @property
    def edge_count(self) -> int:
        return self._edge_count

    async def load_graph(self, network_type: ENetworkType, bbox: DBoundingBox) -> None:
        logger.info("Loading road graph from database")
        edges = await self._road_graph_repository.get_edges_in_bbox(network_type, bbox)
        self.load_from_edges(edges)
        logger.info(
            "Road graph loaded",
            extra={"nodes": self.node_count, "edges": self.edge_count},
        )

    def load_from_edges(self, edges: Iterable[DRoadEdgeRow]) -> None:
        coordinates: dict[int, tuple[float, float]] = {}
        adjacency: dict[int, list[DNeighbor]] = {}
        best_distance: dict[tuple[int, int], float] = {}

        for edge in edges:
            coordinates[edge.from_node_id] = (edge.from_latitude, edge.from_longitude)
            coordinates[edge.to_node_id] = (edge.to_latitude, edge.to_longitude)

            key = (edge.from_node_id, edge.to_node_id)
            current = best_distance.get(key)
            if current is None or edge.distance_meter < current:
                best_distance[key] = edge.distance_meter

        for (from_node_id, to_node_id), distance in best_distance.items():
            adjacency.setdefault(from_node_id, []).append(
                DNeighbor(node_id=to_node_id, distance_meter=distance)
            )

        self._coordinates = coordinates
        self._adjacency = adjacency
        self._edge_count = len(best_distance)
        self._node_ids = np.fromiter(coordinates.keys(), dtype=np.int64)
        self._latitudes = np.array([c[0] for c in coordinates.values()], dtype=np.float64)
        self._longitudes = np.array(
            [c[1] for c in coordinates.values()], dtype=np.float64
        )

    def node_ids(self) -> list[int]:
        return list(self._coordinates)

    def has_node(self, node_id: int) -> bool:
        return node_id in self._coordinates

    def coordinates(self, node_id: int) -> tuple[float, float]:
        return self._coordinates[node_id]

    def haversine(self, node_a: int, node_b: int) -> float:
        lat_a, lon_a = self._coordinates[node_a]
        lat_b, lon_b = self._coordinates[node_b]
        return haversine_distance(lat_a, lon_a, lat_b, lon_b)

    def nearest_node(self, latitude: float, longitude: float) -> DNearestNode | None:
        if self.node_count == 0:
            return None

        distances = haversine_distances(
            latitude, longitude, self._latitudes, self._longitudes
        )
        index = int(np.argmin(distances))
        return DNearestNode(
            node_id=int(self._node_ids[index]),
            distance_meter=float(distances[index]),
        )

    def neighbors(self, node_id: int) -> list[DNeighbor]:
        return self._adjacency.get(node_id, [])
