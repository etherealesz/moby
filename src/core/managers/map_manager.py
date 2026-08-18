import os
import osmnx as ox
import networkx as nx
from typing import Dict
from injector import inject, Binder, Module, singleton
from infrastructures.databases.master import DatabaseMasterSessionMaker


class MapManager:
    """
    Manager singleton untuk mengelola dan memuat graph jaringan jalan (OSMnx)
    ke dalam memori (RAM) agar pencarian rute A* berjalan secara instan (milidetik).
    """

    @inject
    def __init__(self, session_maker: DatabaseMasterSessionMaker):
        self._session_maker = session_maker
        self.maps_dir = "maps_cache"
        os.makedirs(self.maps_dir, exist_ok=True)
        # Dictionary untuk menyimpan graph di RAM: { "city_mode": graph }
        self._graphs: Dict[str, nx.MultiDiGraph] = {}

    def load_all_graphs(self) -> None:
        """
        Memuat seluruh file .graphml yang ada di folder maps_cache ke dalam RAM.
        Dipanggil saat startup aplikasi (FastAPI lifespan).
        """
        print("\n=== [MapManager] Memulai pemuatan peta ke memori RAM ===")
        if not os.path.exists(self.maps_dir):
            return

        for filename in os.listdir(self.maps_dir):
            if filename.endswith(".graphml"):
                # Contoh nama file: bbox_106.82_-6.2_106.83_-6.17_walk.graphml
                # Atau lembang_walk.graphml
                key = filename.replace(".graphml", "")
                filepath = os.path.join(self.maps_dir, filename)
                print(f"  -> Memuat {filename} ke memori...")
                try:
                    self._graphs[key] = ox.load_graphml(filepath)
                    print(
                        f"     ✓ Sukses. Nodes: {len(self._graphs[key].nodes)}, Edges: {len(self._graphs[key].edges)}"
                    )
                except Exception as e:
                    print(f"     ✗ Gagal memuat {filename}: {e}")
        print("=== [MapManager] Selesai memuat peta ke RAM ===\n")

    def get_graph(self, key: str) -> nx.MultiDiGraph | None:
        """
        Mengambil graph dari RAM. Jika belum ada di RAM tetapi ada di disk,
        maka akan dimuat secara dinamis ke RAM.
        """
        if key in self._graphs:
            return self._graphs[key]

        # Coba muat dari disk jika filenya ada
        filepath = os.path.join(self.maps_dir, f"{key}.graphml")
        if os.path.exists(filepath):
            print(f"[MapManager] Memuat peta secara dinamis dari disk: {filepath}")
            try:
                self._graphs[key] = ox.load_graphml(filepath)
                return self._graphs[key]
            except Exception as e:
                print(f"[MapManager] Gagal memuat peta dari disk: {e}")

        return None

    def register_graph(self, key: str, graph: nx.MultiDiGraph) -> None:
        """
        Mendaftarkan graph baru ke RAM dan menyimpannya ke disk.
        """
        self._graphs[key] = graph
        filepath = os.path.join(self.maps_dir, f"{key}.graphml")
        ox.save_graphml(graph, filepath)
        print(f"[MapManager] Graph '{key}' berhasil disimpan ke disk & memori.")

    async def get_graph_from_db(self, network_type: str) -> nx.MultiDiGraph | None:
        """
        Mengambil graph dari RAM. Jika belum ada di RAM, dimuat dari database lokal.
        """
        key = f"db_{network_type}"
        if key in self._graphs:
            return self._graphs[key]

        print(f"[MapManager] Memuat graph '{network_type}' dari database local...")
        async with self._session_maker() as session:
            from sqlalchemy import text
            import shapely.wkt

            # Query all nodes using raw sql for maximum speed
            node_result = await session.execute(
                text(
                    "SELECT id, lat, lon FROM osm_nodes WHERE network_type = :network_type"
                ),
                {"network_type": network_type},
            )
            nodes_data = node_result.fetchall()

            if not nodes_data:
                print(
                    f"[MapManager] Tidak ada data node untuk network_type: {network_type} di database."
                )
                return None

            # Query all edges using raw sql for maximum speed
            edge_result = await session.execute(
                text(
                    "SELECT u, v, key, length, name, highway, oneway, geometry_wkt, maxspeed FROM osm_edges WHERE network_type = :network_type"
                ),
                {"network_type": network_type},
            )
            edges_data = edge_result.fetchall()

            # Reconstruct NetworkX MultiDiGraph
            graph = nx.MultiDiGraph()
            graph.graph["crs"] = "epsg:4326"

            # Bulk add nodes
            for node_id, lat, lon in nodes_data:
                graph.add_node(node_id, y=lat, x=lon)

            # Bulk add edges
            for (
                u,
                v,
                e_key,
                length,
                name,
                highway,
                oneway,
                geometry_wkt,
                maxspeed,
            ) in edges_data:
                edge_attrs = {
                    "length": length,
                    "name": name,
                    "highway": highway,
                    "oneway": oneway,
                    "maxspeed": maxspeed,
                }
                if geometry_wkt:
                    try:
                        edge_attrs["geometry"] = shapely.wkt.loads(geometry_wkt)
                    except Exception:
                        pass

                graph.add_edge(u, v, key=e_key, **edge_attrs)

            self._graphs[key] = graph
            print(
                f"[MapManager] Berhasil memuat graph '{network_type}' dari database. Nodes: {len(graph.nodes)}, Edges: {len(graph.edges)}"
            )
            return graph

    async def load_all_graphs_from_db(self) -> None:
        """
        Memuat seluruh graph dari database ke dalam RAM saat startup.
        """
        print("\n=== [MapManager] Memulai pemuatan peta dari database ke memori RAM ===")
        for network_type in ["walk", "drive"]:
            try:
                await self.get_graph_from_db(network_type)
            except Exception as e:
                print(f"     ✗ Gagal memuat graph '{network_type}' dari database: {e}")
        print("=== [MapManager] Selesai memuat peta dari database ke RAM ===\n")


class CMapManagerModule(Module):
    def configure(self, binder: Binder) -> None:
        binder.bind(MapManager, to=MapManager, scope=singleton)
