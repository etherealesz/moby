import math
import random
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import networkx as nx
import pytest

from core.enums.network_type import ENetworkType
from core.enums.waste_category import EWasteCategory
from core.utils.geo_helper import EARTH_RADIUS_METER, haversine_distance
from modules.facilities.models.facility import Facility
from modules.navigation.exceptions.navigation import (
    FacilityNotFoundError,
    LocationOutOfCoverageError,
)
from modules.navigation.repositories.road_graph.dto import DRoadEdgeRow
from modules.navigation.services.navigation_service.service import NavigationService
from modules.navigation.services.road_graph_manager.service import RoadGraphManager

BASE_LAT, BASE_LON = -6.2, 106.8


def build_random_road_graph(
    node_count: int = 400,
    seed: int = 7,
) -> tuple[list[DRoadEdgeRow], nx.DiGraph]:
    rng = random.Random(seed)
    coords = {
        node_id: (
            BASE_LAT + rng.uniform(-0.0135, 0.0135),
            BASE_LON + rng.uniform(-0.0135, 0.0135),
        )
        for node_id in range(1, node_count + 1)
    }

    rows: list[DRoadEdgeRow] = []
    reference = nx.DiGraph()
    for node_id, (lat, lon) in coords.items():
        nearest = sorted(
            (haversine_distance(lat, lon, *coords[other]), other)
            for other in coords
            if other != node_id
        )[:4]
        for straight, other in nearest:
            weight = round(straight * rng.uniform(1.0, 1.4), 2) + 0.01
            directions = [(node_id, other)]
            if rng.random() > 0.15:
                directions.append((other, node_id))
            for u, v in directions:
                if reference.has_edge(u, v) and reference[u][v]["weight"] <= weight:
                    continue
                reference.add_edge(u, v, weight=weight)
                rows.append(DRoadEdgeRow(u, v, weight, *coords[u], *coords[v]))
    return rows, reference


def build_service(rows: list[DRoadEdgeRow]) -> NavigationService:
    manager = RoadGraphManager(road_graph_repository=MagicMock())
    manager.load_from_edges(rows)
    return NavigationService(facility_repository=MagicMock(), road_graph_manager=manager)


def test_haversine_one_degree_on_equator():
    expected = 2 * math.pi * EARTH_RADIUS_METER / 360
    assert haversine_distance(0.0, 0.0, 0.0, 1.0) == pytest.approx(expected, rel=1e-9)
    assert haversine_distance(0.0, 0.0, 1.0, 0.0) == pytest.approx(expected, rel=1e-9)
    assert haversine_distance(BASE_LAT, BASE_LON, BASE_LAT, BASE_LON) == 0.0


def test_astar_and_dijkstra_match_networkx():
    rows, reference = build_random_road_graph()
    service = build_service(rows)
    rng = random.Random(1)
    nodes = list(reference.nodes)

    checked = 0
    for _ in range(60):
        start, goal = rng.sample(nodes, 2)
        astar = service.astar(start, goal)
        dijkstra = service.dijkstra(start, goal)

        if not nx.has_path(reference, start, goal):
            assert astar.path == [] and dijkstra.path == []
            continue

        expected = nx.dijkstra_path_length(reference, start, goal, weight="weight")
        assert astar.distance_meter == pytest.approx(expected, abs=1e-6)
        assert dijkstra.distance_meter == pytest.approx(expected, abs=1e-6)
        assert astar.path[0] == start and astar.path[-1] == goal
        assert sum(
            reference[u][v]["weight"] for u, v in zip(astar.path, astar.path[1:])
        ) == pytest.approx(expected, abs=1e-6)
        assert astar.explored_nodes <= dijkstra.explored_nodes
        checked += 1

    assert checked > 30


def test_astar_matches_networkx_astar():
    rows, reference = build_random_road_graph(seed=11)
    service = build_service(rows)
    manager = service.road_graph_manager
    rng = random.Random(2)
    nodes = list(reference.nodes)

    for _ in range(20):
        start, goal = rng.sample(nodes, 2)
        if not nx.has_path(reference, start, goal):
            continue
        expected = nx.astar_path_length(
            reference,
            start,
            goal,
            heuristic=lambda a, b: manager.haversine(a, b),
            weight="weight",
        )
        assert service.astar(start, goal).distance_meter == pytest.approx(expected)


def test_astar_returns_empty_path_when_unreachable():
    rows = [
        DRoadEdgeRow(1, 2, 10.0, BASE_LAT, BASE_LON, BASE_LAT, BASE_LON + 0.0001),
        DRoadEdgeRow(
            3, 4, 10.0, BASE_LAT + 0.01, BASE_LON, BASE_LAT + 0.01, BASE_LON + 0.0001
        ),
    ]
    result = build_service(rows).astar(1, 4)
    assert result.path == []
    assert math.isinf(result.distance_meter)


def test_road_graph_manager_neighbors_and_nearest_node():
    rows = [
        DRoadEdgeRow(1, 2, 15.0, BASE_LAT, BASE_LON, BASE_LAT, BASE_LON + 0.0001),
        DRoadEdgeRow(1, 2, 12.0, BASE_LAT, BASE_LON, BASE_LAT, BASE_LON + 0.0001),
        DRoadEdgeRow(
            2, 3, 11.0, BASE_LAT, BASE_LON + 0.0001, BASE_LAT, BASE_LON + 0.0002
        ),
    ]
    manager = RoadGraphManager(road_graph_repository=MagicMock())
    manager.load_from_edges(rows)

    assert manager.neighbors(1) == [(2, 12.0)]
    assert manager.neighbors(3) == []
    assert manager.node_count == 3 and manager.edge_count == 2

    nearest = manager.nearest_node(BASE_LAT + 0.00001, BASE_LON + 0.00021)
    assert nearest.node_id == 3
    assert nearest.distance_meter < 5


def make_facility(facility_id: int, lat: float, lon: float) -> Facility:
    return Facility(
        facility_id=facility_id,
        facility_name=f"Fasilitas {facility_id}",
        facility_type="Bank Sampah",
        latitude=Decimal(str(lat)),
        longitude=Decimal(str(lon)),
        address=None,
        city="Jakarta",
    )


def grid_rows(size: int = 10, spacing: float = 0.001) -> list[DRoadEdgeRow]:
    def node(i: int, j: int) -> tuple[int, float, float]:
        return i * size + j + 1, BASE_LAT + i * spacing, BASE_LON + j * spacing

    rows = []
    for i in range(size):
        for j in range(size):
            for di, dj in ((0, 1), (1, 0)):
                if i + di >= size or j + dj >= size:
                    continue
                a, a_lat, a_lon = node(i, j)
                b, b_lat, b_lon = node(i + di, j + dj)
                length = haversine_distance(a_lat, a_lon, b_lat, b_lon)
                rows.append(DRoadEdgeRow(a, b, length, a_lat, a_lon, b_lat, b_lon))
                rows.append(DRoadEdgeRow(b, a, length, b_lat, b_lon, a_lat, a_lon))
    return rows


async def test_find_route_picks_shortest_candidate():
    facility_repository = MagicMock()
    facility_repository.get_by_category = AsyncMock(
        return_value=[
            make_facility(1, BASE_LAT + 0.008, BASE_LON + 0.008),
            make_facility(2, BASE_LAT + 0.002, BASE_LON + 0.001),
        ]
    )
    road_graph_repository = MagicMock()
    road_graph_repository.get_edges_in_bbox = AsyncMock(return_value=grid_rows())
    service = NavigationService(
        facility_repository=facility_repository,
        road_graph_manager=RoadGraphManager(road_graph_repository=road_graph_repository),
    )

    result = await service.find_route(
        BASE_LAT, BASE_LON, EWasteCategory.ANORGANIK, ENetworkType.WALK
    )

    assert result.facility.facility_id == 2
    assert result.route[0] == pytest.approx((BASE_LAT, BASE_LON))
    assert result.route[-1] == pytest.approx((BASE_LAT + 0.002, BASE_LON + 0.001))
    expected = haversine_distance(BASE_LAT, BASE_LON, BASE_LAT + 0.002, BASE_LON) + (
        haversine_distance(BASE_LAT, BASE_LON, BASE_LAT, BASE_LON + 0.001)
    )
    assert result.distance_meter == pytest.approx(expected, rel=1e-3)
    assert {c.facility.facility_id for c in result.candidates} == {1, 2}
    road_graph_repository.get_edges_in_bbox.assert_awaited_once()

    chosen = await service.find_route(
        BASE_LAT, BASE_LON, EWasteCategory.ANORGANIK, ENetworkType.WALK, facility_id=1
    )
    assert chosen.facility.facility_id == 1
    assert [c.facility.facility_id for c in chosen.candidates] == [1]

    with pytest.raises(FacilityNotFoundError):
        await service.find_route(
            BASE_LAT, BASE_LON, EWasteCategory.ANORGANIK, ENetworkType.WALK, facility_id=99
        )


async def test_find_route_without_facility_raises():
    facility_repository = MagicMock()
    facility_repository.get_by_category = AsyncMock(return_value=[])
    service = NavigationService(
        facility_repository=facility_repository,
        road_graph_manager=RoadGraphManager(road_graph_repository=MagicMock()),
    )

    with pytest.raises(FacilityNotFoundError):
        await service.find_route(BASE_LAT, BASE_LON, EWasteCategory.B3, ENetworkType.WALK)


async def test_find_route_user_far_from_graph_raises():
    facility_repository = MagicMock()
    facility_repository.get_by_category = AsyncMock(
        return_value=[make_facility(1, BASE_LAT + 0.002, BASE_LON)]
    )
    road_graph_repository = MagicMock()
    road_graph_repository.get_edges_in_bbox = AsyncMock(return_value=grid_rows())
    service = NavigationService(
        facility_repository=facility_repository,
        road_graph_manager=RoadGraphManager(road_graph_repository=road_graph_repository),
    )

    with pytest.raises(LocationOutOfCoverageError):
        await service.find_route(
            BASE_LAT - 0.02, BASE_LON, EWasteCategory.ANORGANIK, ENetworkType.WALK
        )
