import osmnx as ox
from injector import inject
from core.algorithms.astar import custom_astar_search
from core.managers.map_manager import MapManager

class FindRouteUseCase:
    @inject
    def __init__(self, map_manager: MapManager):
        self._map_manager = map_manager

    async def execute(self, start_lat: float, start_lon: float, end_lat: float, end_lon: float, mode: str) -> dict:
        """
        Mencari rute jalan nyata terpendek antara titik awal dan akhir menggunakan A* Search.
        Menggunakan MapManager untuk mengambil peta dari memori RAM instan.
        
        Args:
            start_lat: Latitude awal
            start_lon: Longitude awal
            end_lat: Latitude akhir
            end_lon: Longitude akhir
            mode: "walk" (pejalan kaki) atau "drive" (mobil/motor)
        """
        # Validasi mode
        if mode not in ["walk", "drive"]:
            mode = "walk"

        # Ambil graph dari MapManager (yang dimuat dari database lokal ke RAM)
        graph = await self._map_manager.get_graph_from_db(mode)
        
        # Jika belum ada data di database
        if graph is None:
            raise Exception(
                f"Data jaringan jalan untuk mode '{mode}' belum diimpor ke database local. "
                "Silakan jalankan seeder terlebih dahulu dengan perintah: "
                "uv run python -m scripts.commands run import_osm"
            )
            
        print(f"[FindRouteUseCase] Graph siap digunakan dari DB cache. Nodes: {len(graph.nodes)}, Edges: {len(graph.edges)}")

        # Cari node jalan terdekat di graph dari titik awal (start) dan akhir (goal)
        # Cast ke standard Python int untuk menghindari masalah serialisasi NumPy types di Pydantic
        start_node = int(ox.nearest_nodes(graph, X=start_lon, Y=start_lat))
        goal_node = int(ox.nearest_nodes(graph, X=end_lon, Y=end_lat))
        
        # Verifikasi jarak koordinat input ke node terdekat (maksimal 5 km)
        # Ini mencegah pencarian rute yang tidak relevan di luar area cakupan Jakarta/Lembang
        from core.algorithms.astar import haversine_distance
        start_node_data = graph.nodes[start_node]
        goal_node_data = graph.nodes[goal_node]
        
        dist_to_start = haversine_distance(start_lat, start_lon, start_node_data['y'], start_node_data['x'])
        dist_to_goal = haversine_distance(end_lat, end_lon, goal_node_data['y'], goal_node_data['x'])
        
        if dist_to_start > 5000 or dist_to_goal > 5000:
            raise Exception(
                "Koordinat pencarian berada di luar area cakupan peta yang tersedia di database lokal. "
                "Peta lokal saat ini hanya mencakup Jakarta dan Lembang (maksimal radius 5 km)."
            )
        
        # Jalankan algoritma A* Search kustom
        path_nodes, total_distance = custom_astar_search(graph, start_node, goal_node)
        
        if not path_nodes:
            raise Exception("Rute navigasi tidak ditemukan oleh algoritma A*.")
            
        # Konversi node path menjadi list koordinat lat/lon
        route_coordinates = []
        for node_id in path_nodes:
            node_data = graph.nodes[node_id]
            route_coordinates.append([node_data['y'], node_data['x']]) # Format [lat, lon] untuk Leaflet
            
        return {
            "mode": mode,
            "distance_meters": round(total_distance, 2),
            "start_node_id": start_node,
            "goal_node_id": goal_node,
            "route": route_coordinates
        }
