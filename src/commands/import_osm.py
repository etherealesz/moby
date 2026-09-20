import sys
import asyncio
import osmnx as ox
import shapely.wkt
from sqlalchemy import delete, insert
from injector import Injector

from core.logger.factory import create_app_logger
from infrastructures.databases.master import DatabaseMasterSession
from modules.navigation.model import MOSMNode, MOSMEdge

logger = create_app_logger()

ox.settings.timeout = 300
ox.settings.requests_timeout = 300
ox.settings.use_cache = False


DEFAULT_TARGET_PLACES = [
    "DKI Jakarta, Indonesia",
    "Kota Depok, Jawa Barat, Indonesia",
    "Kota Tangerang, Banten, Indonesia",
    "Kota Bekasi, Jawa Barat, Indonesia",
]


async def execute(injector: Injector, args: list[str] | None = None):
    session = injector.get(DatabaseMasterSession)

    if args is None:
        args = sys.argv[3:]

    place = None
    mode = None
    clean = False
    combined = True

    for idx, arg in enumerate(args):
        if arg == "--place" and idx + 1 < len(args):
            place = args[idx + 1]
        elif arg == "--mode" and idx + 1 < len(args):
            mode = args[idx + 1]
        elif arg == "--clean":
            clean = True
        elif arg == "--separate":
            combined = False

    modes = ["drive"]
    if mode:
        if mode.lower() in ["all", "both"]:
            modes = ["walk", "drive"]
        else:
            modes = [mode]

    if place:
        places_to_import = [place]
        for m in modes:
            await import_place_network(session, places_to_import, m, clean_mode=clean)
            await asyncio.sleep(2)
    else:
        if combined:
            for m in modes:
                await import_place_network(
                    session, DEFAULT_TARGET_PLACES, m, clean_mode=clean
                )
                await asyncio.sleep(2)
        else:
            for m in modes:
                for p in DEFAULT_TARGET_PLACES:
                    await import_place_network(session, [p], m, clean_mode=clean)
                    await asyncio.sleep(2)


async def import_place_network(
    session: DatabaseMasterSession,
    places: list[str] | str,
    mode: str,
    clean_mode: bool = False,
):
    place_label = ", ".join(places) if isinstance(places, list) else places
    logger.info(f"Mulai mengunduh peta OSM untuk: [{place_label}] | Mode: '{mode}'...")
    try:
        if isinstance(places, list) and len(places) == 1:
            target = places[0]
        else:
            target = places

        graph = ox.graph_from_place(target, network_type=mode)
        logger.info(
            f"Peta terunduh. Nodes: {len(graph.nodes)}, Edges: {len(graph.edges)}"
        )
    except Exception as e:
        logger.error(f"Gagal mengunduh peta dari OpenStreetMap: {e}")
        return

    nodes_data = []
    for node_id, data in graph.nodes(data=True):
        nodes_data.append(
            {
                "id": int(node_id),
                "lat": float(data["y"]),
                "lon": float(data["x"]),
                "network_type": mode,
            }
        )

    edges_data = []
    for u, v, key, data in graph.edges(keys=True, data=True):
        geometry_wkt = None
        if "geometry" in data:
            geometry_wkt = shapely.wkt.dumps(data["geometry"])

        edges_data.append(
            {
                "u": int(u),
                "v": int(v),
                "key": int(key),
                "network_type": mode,
                "length": float(data.get("length", 0.0)),
                "name": str(data.get("name")) if data.get("name") else None,
                "highway": str(data.get("highway")) if data.get("highway") else None,
                "oneway": bool(data.get("oneway")) if "oneway" in data else None,
                "geometry_wkt": geometry_wkt,
                "maxspeed": str(data.get("maxspeed")) if data.get("maxspeed") else None,
            }
        )

    logger.info(
        f"Menyimpan {len(nodes_data)} nodes dan {len(edges_data)} edges ke database local..."
    )

    async with session.begin():
        chunk_size = 5000

        if clean_mode:
            logger.info(f"Membersihkan seluruh data lama untuk mode '{mode}'...")
            await session.execute(
                delete(MOSMEdge).where(MOSMEdge.network_type == mode)
            )
            await session.execute(
                delete(MOSMNode).where(MOSMNode.network_type == mode)
            )
        else:
            node_ids = [n["id"] for n in nodes_data]
            logger.info("Membersihkan data lama yang bentrok...")
            for i in range(0, len(node_ids), chunk_size):
                chunk = node_ids[i : i + chunk_size]
                await session.execute(
                    delete(MOSMEdge).where(
                        (MOSMEdge.network_type == mode)
                        & (MOSMEdge.u.in_(chunk) | MOSMEdge.v.in_(chunk))
                    )
                )
                await session.execute(
                    delete(MOSMNode).where(
                        (MOSMNode.network_type == mode) & (MOSMNode.id.in_(chunk))
                    )
                )

        logger.info("Memasukkan data nodes...")
        for i in range(0, len(nodes_data), chunk_size):
            chunk = nodes_data[i : i + chunk_size]
            await session.execute(insert(MOSMNode), chunk)

        logger.info("Memasukkan data edges...")
        for i in range(0, len(edges_data), chunk_size):
            chunk = edges_data[i : i + chunk_size]
            await session.execute(insert(MOSMEdge), chunk)

    logger.info(
        f"Sukses mengimpor peta untuk [{place_label}] | Mode: '{mode}' ke database.\n"
    )
