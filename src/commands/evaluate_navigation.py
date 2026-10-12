import argparse
import csv
import json
import math
import random
import statistics
from datetime import datetime
from pathlib import Path

from injector import Injector

from core.config.settings import settings
from core.constants.paths import PROJECT_ROOT, REPORTS_DIR
from core.enums.network_type import ENetworkType
from core.logger.factory import create_app_logger
from modules.navigation.repositories.road_graph.dto import DBoundingBox
from modules.navigation.services.navigation_service.service import NavigationService

logger = create_app_logger()

METERS_PER_DEGREE_LATITUDE = 111_320.0


async def execute(injector: Injector, args: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="evaluate_navigation")
    parser.add_argument(
        "--network-type",
        choices=[e.value for e in ENetworkType],
        default=ENetworkType.WALK.value,
    )
    parser.add_argument("--pairs", type=Path, default=None)
    parser.add_argument("--random", type=int, default=0)
    parser.add_argument("--center", type=float, nargs=2, metavar=("LAT", "LON"))
    parser.add_argument("--radius", type=float, default=3000.0, help="meter")
    parser.add_argument("--seed", type=int, default=42)
    options = parser.parse_args(args or [])

    network_type = ENetworkType(options.network_type)
    if options.pairs:
        rows = await _evaluate_pairs_file(injector, options.pairs, network_type)
    elif options.random and options.center:
        rows = await _evaluate_random_pairs(
            injector,
            network_type,
            count=options.random,
            center=(options.center[0], options.center[1]),
            radius=options.radius,
            seed=options.seed,
        )
    else:
        parser.error("Gunakan --pairs FILE atau --random N --center LAT LON")
        return

    _write_reports(rows, network_type)


async def _evaluate_pairs_file(
    injector: Injector,
    pairs_path: Path,
    network_type: ENetworkType,
) -> list[dict]:
    if not pairs_path.is_absolute():
        pairs_path = PROJECT_ROOT / pairs_path

    rows: list[dict] = []
    with open(pairs_path, newline="", encoding="utf-8-sig") as file:
        for index, pair in enumerate(csv.DictReader(file), start=1):
            origin = (float(pair["origin_lat"]), float(pair["origin_lon"]))
            destination = (float(pair["dest_lat"]), float(pair["dest_lon"]))

            service = injector.get(NavigationService)
            graph = service.road_graph_manager
            bbox = DBoundingBox.from_points(
                [origin, destination], settings.navigation.bbox_padding_degree
            )
            await graph.load_graph(network_type, bbox)

            start = graph.nearest_node(*origin)
            goal = graph.nearest_node(*destination)
            if start is None or goal is None:
                logger.warning(f"Pasangan {index}: tidak ada simpul graf di area ini")
                continue

            rows.append(
                _compare(service, start.node_id, goal.node_id, pair.get("label") or index)
            )
    return rows


async def _evaluate_random_pairs(
    injector: Injector,
    network_type: ENetworkType,
    count: int,
    center: tuple[float, float],
    radius: float,
    seed: int,
) -> list[dict]:
    lat_delta = radius / METERS_PER_DEGREE_LATITUDE
    lon_delta = radius / (METERS_PER_DEGREE_LATITUDE * math.cos(math.radians(center[0])))
    bbox = DBoundingBox(
        min_latitude=center[0] - lat_delta,
        min_longitude=center[1] - lon_delta,
        max_latitude=center[0] + lat_delta,
        max_longitude=center[1] + lon_delta,
    )

    service = injector.get(NavigationService)
    graph = service.road_graph_manager
    await graph.load_graph(network_type, bbox)
    if graph.node_count < 2:
        raise RuntimeError("Graf di area ini kosong. Jalankan extract_road_graph dulu.")

    node_ids = sorted(graph.node_ids())
    rng = random.Random(seed)
    rows: list[dict] = []
    for index in range(1, count + 1):
        start, goal = rng.sample(node_ids, 2)
        rows.append(_compare(service, start, goal, index))
    return rows


def _compare(service: NavigationService, start: int, goal: int, label) -> dict:
    astar = service.astar(start, goal)
    dijkstra = service.dijkstra(start, goal)
    found = bool(astar.path) and bool(dijkstra.path)

    return {
        "label": label,
        "start_node_id": start,
        "goal_node_id": goal,
        "straight_distance_meter": round(
            service.road_graph_manager.haversine(start, goal), 2
        ),
        "route_found": found,
        "astar_distance_meter": round(astar.distance_meter, 2) if astar.path else None,
        "dijkstra_distance_meter": (
            round(dijkstra.distance_meter, 2) if dijkstra.path else None
        ),
        "same_distance": (
            math.isclose(astar.distance_meter, dijkstra.distance_meter, abs_tol=0.01)
            if found
            else None
        ),
        "astar_path_nodes": len(astar.path),
        "dijkstra_path_nodes": len(dijkstra.path),
        "astar_explored_nodes": astar.explored_nodes,
        "dijkstra_explored_nodes": dijkstra.explored_nodes,
        "astar_time_ms": round(astar.computation_time_ms, 3),
        "dijkstra_time_ms": round(dijkstra.computation_time_ms, 3),
    }


def _write_reports(rows: list[dict], network_type: ENetworkType) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = REPORTS_DIR / f"navigation_comparison_{network_type.value}.csv"
    json_path = REPORTS_DIR / f"navigation_comparison_{network_type.value}.json"

    if rows:
        with open(csv_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    found = [row for row in rows if row["route_found"]]

    def mean(key: str) -> float | None:
        return round(statistics.mean(row[key] for row in found), 3) if found else None

    summary = {
        "generated_at": datetime.now().isoformat(),
        "network_type": network_type.value,
        "pairs": len(rows),
        "routes_found": len(found),
        "same_distance_ratio": (
            round(sum(1 for row in found if row["same_distance"]) / len(found), 4)
            if found
            else None
        ),
        "mean_astar_explored_nodes": mean("astar_explored_nodes"),
        "mean_dijkstra_explored_nodes": mean("dijkstra_explored_nodes"),
        "mean_astar_time_ms": mean("astar_time_ms"),
        "mean_dijkstra_time_ms": mean("dijkstra_time_ms"),
        "mean_route_distance_meter": mean("astar_distance_meter"),
    }
    json_path.write_text(
        json.dumps({"summary": summary, "pairs": rows}, indent=2), encoding="utf-8"
    )
    logger.info(f"Hasil evaluasi navigasi: {csv_path} dan {json_path}")
    logger.info(json.dumps(summary, indent=2))
