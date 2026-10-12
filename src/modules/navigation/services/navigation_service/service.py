import heapq
import time

from injector import inject

from core.config.settings import settings
from core.enums.network_type import ENetworkType
from core.enums.waste_category import EWasteCategory
from core.logger.factory import create_app_logger
from core.utils.geo_helper import haversine_distance
from modules.facilities.models.facility import Facility
from modules.facilities.repositories.facility.protocol import FacilityRepository
from modules.navigation.exceptions.navigation import (
    FacilityNotFoundError,
    FacilityOutOfRangeError,
    LocationOutOfCoverageError,
    RoadGraphNotAvailableError,
    RouteNotFoundError,
)
from modules.navigation.repositories.road_graph.dto import DBoundingBox
from modules.navigation.services.navigation_service.dto import (
    DCandidateRoute,
    DRouteResult,
    DSearchResult,
)
from modules.navigation.services.road_graph_manager.service import RoadGraphManager

logger = create_app_logger()


class NavigationService:
    @inject
    def __init__(
        self,
        facility_repository: FacilityRepository,
        road_graph_manager: RoadGraphManager,
    ) -> None:
        self._facility_repository = facility_repository
        self._road_graph_manager = road_graph_manager

    @property
    def road_graph_manager(self) -> RoadGraphManager:
        return self._road_graph_manager

    async def get_candidate_facilities(self, category: EWasteCategory) -> list[Facility]:
        return await self._facility_repository.get_by_category(category)

    async def find_route(
        self,
        user_lat: float,
        user_lon: float,
        category: EWasteCategory,
        network_type: ENetworkType,
    ) -> DRouteResult:
        nav_config = settings.navigation

        facilities = await self.get_candidate_facilities(category)
        if not facilities:
            raise FacilityNotFoundError

        candidates = self._select_nearest_facilities(user_lat, user_lon, facilities)
        if not candidates:
            raise FacilityOutOfRangeError

        points = [(user_lat, user_lon)] + [
            (float(f.latitude), float(f.longitude)) for f, _ in candidates
        ]
        bbox = DBoundingBox.from_points(points, nav_config.bbox_padding_degree)

        load_start = time.perf_counter()
        await self._road_graph_manager.load_graph(network_type, bbox)
        graph_load_time_ms = (time.perf_counter() - load_start) * 1000
        if self._road_graph_manager.node_count == 0:
            raise RoadGraphNotAvailableError

        start = self._road_graph_manager.nearest_node(user_lat, user_lon)
        if start is None or start.distance_meter > nav_config.max_snap_distance_meter:
            raise LocationOutOfCoverageError

        best: tuple[Facility, DSearchResult] | None = None
        candidate_routes: list[DCandidateRoute] = []
        for facility, straight_distance in candidates:
            goal = self._road_graph_manager.nearest_node(
                float(facility.latitude), float(facility.longitude)
            )
            if goal is None or goal.distance_meter > nav_config.max_snap_distance_meter:
                candidate_routes.append(
                    DCandidateRoute(
                        facility_id=facility.facility_id,
                        straight_distance_meter=straight_distance,
                        route_distance_meter=None,
                        explored_nodes=0,
                        computation_time_ms=0.0,
                    )
                )
                continue

            result = self.astar(start.node_id, goal.node_id)
            candidate_routes.append(
                DCandidateRoute(
                    facility_id=facility.facility_id,
                    straight_distance_meter=straight_distance,
                    route_distance_meter=result.distance_meter if result.path else None,
                    explored_nodes=result.explored_nodes,
                    computation_time_ms=result.computation_time_ms,
                )
            )
            if result.path and (
                best is None or result.distance_meter < best[1].distance_meter
            ):
                best = (facility, result)

        if best is None:
            raise RouteNotFoundError

        facility, result = best
        route = [self._road_graph_manager.coordinates(node_id) for node_id in result.path]
        return DRouteResult(
            facility=facility,
            network_type=network_type,
            route=route,
            distance_meter=result.distance_meter,
            explored_nodes=sum(c.explored_nodes for c in candidate_routes),
            computation_time_ms=sum(c.computation_time_ms for c in candidate_routes),
            graph_load_time_ms=graph_load_time_ms,
            graph_node_count=self._road_graph_manager.node_count,
            graph_edge_count=self._road_graph_manager.edge_count,
            candidates=candidate_routes,
        )

    def astar(self, start: int, goal: int) -> DSearchResult:
        return self._search(start, goal, use_heuristic=True)

    def dijkstra(self, start: int, goal: int) -> DSearchResult:
        return self._search(start, goal, use_heuristic=False)

    def _search(self, start: int, goal: int, use_heuristic: bool) -> DSearchResult:
        graph = self._road_graph_manager
        started_at = time.perf_counter()

        def h(node_id: int) -> float:
            return graph.haversine(node_id, goal) if use_heuristic else 0.0

        g_score: dict[int, float] = {start: 0.0}
        parent: dict[int, int] = {}
        open_list: list[tuple[float, float, int]] = [(h(start), 0.0, start)]
        closed_list: set[int] = set()

        while open_list:
            _, g_current, current = heapq.heappop(open_list)
            if current in closed_list:
                continue

            if current == goal:
                path = [current]
                while path[-1] != start:
                    path.append(parent[path[-1]])
                path.reverse()
                return DSearchResult(
                    path=path,
                    distance_meter=g_current,
                    explored_nodes=len(closed_list) + 1,
                    computation_time_ms=(time.perf_counter() - started_at) * 1000,
                )

            closed_list.add(current)

            for neighbor in graph.neighbors(current):
                if neighbor.node_id in closed_list:
                    continue
                tentative_g = g_current + neighbor.distance_meter
                if tentative_g < g_score.get(neighbor.node_id, float("inf")):
                    parent[neighbor.node_id] = current
                    g_score[neighbor.node_id] = tentative_g
                    f = tentative_g + h(neighbor.node_id)
                    heapq.heappush(open_list, (f, tentative_g, neighbor.node_id))

        return DSearchResult(
            path=[],
            distance_meter=float("inf"),
            explored_nodes=len(closed_list),
            computation_time_ms=(time.perf_counter() - started_at) * 1000,
        )

    def _select_nearest_facilities(
        self,
        user_lat: float,
        user_lon: float,
        facilities: list[Facility],
    ) -> list[tuple[Facility, float]]:
        nav_config = settings.navigation
        with_distance = [
            (
                facility,
                haversine_distance(
                    user_lat,
                    user_lon,
                    float(facility.latitude),
                    float(facility.longitude),
                ),
            )
            for facility in facilities
        ]
        in_range = [
            item
            for item in with_distance
            if item[1] <= nav_config.max_search_radius_meter
        ]
        in_range.sort(key=lambda item: item[1])
        return in_range[: nav_config.max_candidate_facilities]
