import argparse
import json
import time
from datetime import datetime

import osmnx as ox
from injector import Injector
from sqlalchemy import delete, exists, select
from sqlalchemy.dialects.postgresql import insert

from core.constants.paths import REPORTS_DIR
from core.enums.network_type import ENetworkType
from core.logger.factory import create_app_logger
from infrastructures.databases.master import DatabaseMasterSession
from modules.navigation.models.road_edge import RoadEdge
from modules.navigation.models.road_node import RoadNode

logger = create_app_logger()

STUDY_AREA_PLACES = [
    "DKI Jakarta, Indonesia",
    "Kota Tangerang, Banten, Indonesia",
    "Kota Depok, Jawa Barat, Indonesia",
    "Kota Bekasi, Jawa Barat, Indonesia",
]

CHUNK_SIZE = 5000


async def execute(injector: Injector, args: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="extract_road_graph")
    parser.add_argument("--place", action="append", default=None)
    parser.add_argument(
        "--network-type",
        choices=[*(e.value for e in ENetworkType), "all"],
        default="all",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Hapus semua Road_Edge network_type terkait sebelum impor.",
    )
    options = parser.parse_args(args or [])

    ox.settings.use_cache = False
    ox.settings.requests_timeout = 600

    places = options.place or STUDY_AREA_PLACES
    network_types = (
        list(ENetworkType)
        if options.network_type == "all"
        else [ENetworkType(options.network_type)]
    )

    session = injector.get(DatabaseMasterSession)
    summaries = []
    for network_type in network_types:
        summaries.append(
            await _extract_network(session, places, network_type, options.clean)
        )

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / "road_graph_extraction.json"
    report_path.write_text(
        json.dumps(
            {"generated_at": datetime.now().isoformat(), "runs": summaries}, indent=2
        ),
        encoding="utf-8",
    )
    logger.info(f"Ringkasan ditulis ke {report_path}")


async def _extract_network(
    session: DatabaseMasterSession,
    places: list[str],
    network_type: ENetworkType,
    clean: bool,
) -> dict:
    logger.info(f"Mengunduh graf OSM '{network_type}' untuk: {', '.join(places)}")
    started_at = time.perf_counter()
    graph = ox.graph_from_place(places, network_type=network_type.value)
    download_seconds = time.perf_counter() - started_at
    logger.info(
        f"Graf terunduh: {graph.number_of_nodes()} simpul, {graph.number_of_edges()} sisi"
    )

    nodes = [
        {
            "node_id": int(node_id),
            "latitude": round(float(data["y"]), 7),
            "longitude": round(float(data["x"]), 7),
        }
        for node_id, data in graph.nodes(data=True)
    ]

    edges_by_pair: dict[tuple[int, int], dict] = {}
    for u, v, data in graph.edges(data=True):
        key = (int(u), int(v))
        length = round(float(data.get("length", 0.0)), 2)
        oneway = bool(data.get("oneway", False))
        current = edges_by_pair.get(key)
        if current is None or length < current["distance_meter"]:
            edges_by_pair[key] = {
                "from_node_id": key[0],
                "to_node_id": key[1],
                "distance_meter": length,
                "network_type": network_type.value,
                "oneway": oneway,
            }
    edges = list(edges_by_pair.values())

    store_started_at = time.perf_counter()
    async with session.begin():
        if clean:
            await session.execute(
                delete(RoadEdge).where(RoadEdge.network_type == network_type.value)
            )
        else:
            node_ids = [node["node_id"] for node in nodes]
            for i in range(0, len(node_ids), CHUNK_SIZE):
                await session.execute(
                    delete(RoadEdge).where(
                        RoadEdge.network_type == network_type.value,
                        RoadEdge.from_node_id.in_(node_ids[i : i + CHUNK_SIZE]),
                    )
                )

        for i in range(0, len(nodes), CHUNK_SIZE):
            stmt = insert(RoadNode).values(nodes[i : i + CHUNK_SIZE])
            stmt = stmt.on_conflict_do_update(
                index_elements=[RoadNode.node_id],
                set_={
                    "latitude": stmt.excluded.latitude,
                    "longitude": stmt.excluded.longitude,
                },
            )
            await session.execute(stmt)

        for i in range(0, len(edges), CHUNK_SIZE):
            await session.execute(insert(RoadEdge), edges[i : i + CHUNK_SIZE])

        if clean:
            await session.execute(
                delete(RoadNode).where(
                    ~exists(
                        select(RoadEdge.edge_id).where(
                            (RoadEdge.from_node_id == RoadNode.node_id)
                            | (RoadEdge.to_node_id == RoadNode.node_id)
                        )
                    )
                )
            )

    store_seconds = time.perf_counter() - store_started_at
    logger.info(f"Graf '{network_type}' tersimpan ke Road_Node dan Road_Edge")

    return {
        "network_type": network_type.value,
        "places": places,
        "osm_nodes": graph.number_of_nodes(),
        "osm_edges": graph.number_of_edges(),
        "stored_nodes": len(nodes),
        "stored_edges": len(edges),
        "download_seconds": round(download_seconds, 2),
        "store_seconds": round(store_seconds, 2),
        "clean": clean,
    }
