import math
import heapq
import os
import psycopg

# ==========================================
# 1. ALGORITMA A* SEARCH KUSTOM
# ==========================================

def haversine_distance(lat1, lon1, lat2, lon2):
    """Fungsi Heuristik h(n): Jarak garis lurus antara dua koordinat bumi."""
    R = 6371000.0  # Radius bumi dalam meter
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

def custom_astar_search(graph, start_node, goal_node):
    """
    Implementasi Algoritma A* Search di atas graph NetworkX.
    """
    open_set = []
    heapq.heappush(open_set, (0.0, start_node))
    came_from = {}
    
    g_score = {node: float('inf') for node in graph.nodes}
    g_score[start_node] = 0.0
    
    f_score = {node: float('inf') for node in graph.nodes}
    
    goal_lat = graph.nodes[goal_node]['y']
    goal_lon = graph.nodes[goal_node]['x']
    f_score[start_node] = haversine_distance(
        graph.nodes[start_node]['y'], graph.nodes[start_node]['x'],
        goal_lat, goal_lon
    )
    
    open_set_hash = {start_node}
    
    while open_set:
        current_f, current = heapq.heappop(open_set)
        open_set_hash.remove(current)
        
        if current == goal_node:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start_node)
            path.reverse()
            return path, g_score[goal_node]
        
        for neighbor in graph.neighbors(current):
            edge_data = graph.get_edge_data(current, neighbor)
            if edge_data is None:
                continue
            
            # Cari panjang edge terkecil jika ada beberapa jalan paralel
            weight = min(edge.get('length', float('inf')) for edge in edge_data.values())
            
            tentative_g_score = g_score[current] + weight
            
            if tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                
                neighbor_lat = graph.nodes[neighbor]['y']
                neighbor_lon = graph.nodes[neighbor]['x']
                h_score = haversine_distance(neighbor_lat, neighbor_lon, goal_lat, goal_lon)
                
                f_score[neighbor] = tentative_g_score + h_score
                
                if neighbor not in open_set_hash:
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
                    open_set_hash.add(neighbor)
                    
    return None, float('inf')

# ==========================================
# 2. DATABASE INTEGRATION & SEEDING
# ==========================================

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "060905",
    "dbname": "tps_routing_db"
}

def setup_database():
    print("\n--- [1] Memulai Koneksi PostgreSQL ---")
    
    # Hubungkan ke database default 'postgres' dulu untuk membuat db baru jika belum ada
    try:
        conn = psycopg.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            dbname="postgres",
            autocommit=True
        )
        with conn.cursor() as cur:
            # Cek apakah db 'tps_routing_db' sudah ada
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_CONFIG["dbname"],))
            exists = cur.fetchone()
            if not exists:
                print(f"Database '{DB_CONFIG['dbname']}' belum ada. Membuat database baru...")
                cur.execute(f"CREATE DATABASE {DB_CONFIG['dbname']}")
                print("Database berhasil dibuat!")
            else:
                print(f"Database '{DB_CONFIG['dbname']}' sudah ada.")
        conn.close()
    except Exception as e:
        print(f"Gagal menghubungkan ke server PostgreSQL: {e}")
        print("Harap pastikan PostgreSQL di localhost:5432 sudah aktif dengan user 'postgres' dan password '060905'.")
        return False

    # Sekarang hubungkan ke database utama 'tps_routing_db'
    try:
        conn = psycopg.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            dbname=DB_CONFIG["dbname"],
            autocommit=True
        )
        
        with conn.cursor() as cur:
            # Buat tabel TPS
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tps_locations (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    latitude DOUBLE PRECISION NOT NULL,
                    longitude DOUBLE PRECISION NOT NULL,
                    tps_type VARCHAR(100) NOT NULL
                );
            """)
            print("Tabel 'tps_locations' siap (dibuat/sudah ada).")
            
            # Cek apakah sudah ada data
            cur.execute("SELECT COUNT(*) FROM tps_locations;")
            count = cur.fetchone()[0]
            
            if count == 0:
                print("Memasukkan data sampel TPS...")
                sample_data = [
                    ("Dusun bambu", -6.7973820, 107.5746838, "TPS 3R / UPS"),
                    ("Grand Panorama", -6.8105578, 107.6244351, "TPS 3R / UPS"),
                    ("Hotel Pesona Bambu", -6.8122314, 107.6158244, "TPS 3R / UPS"),
                    ("Laxmi Resto", -6.8775000, 107.5717684, "TPS 3R / UPS")
                ]
                cur.executemany("""
                    INSERT INTO tps_locations (name, latitude, longitude, tps_type)
                    VALUES (%s, %s, %s, %s);
                """, sample_data)
                print(f"Berhasil memasukkan {len(sample_data)} data TPS.")
            else:
                print(f"Tabel sudah berisi {count} data TPS. Lewati tahap seeding.")
                
        return conn
    except Exception as e:
        print(f"Gagal menghubungkan atau mengkonfigurasi database '{DB_CONFIG['dbname']}': {e}")
        return False

# ==========================================
# 3. ROUTING & MAP TESTING
# ==========================================

def run_routing_test(db_conn):
    print("\n--- [2] Membaca Data TPS dari Database ---")
    tps_list = []
    with db_conn.cursor() as cur:
        cur.execute("SELECT id, name, latitude, longitude, tps_type FROM tps_locations;")
        rows = cur.fetchall()
        print("Data TPS yang tersimpan di DB:")
        for r in rows:
            print(f" - ID: {r[0]} | {r[1]} ({r[2]}, {r[3]}) | Tipe: {r[4]}")
            tps_list.append({
                "id": r[0],
                "name": r[1],
                "lat": r[2],
                "lon": r[3]
            })

    # Simulasikan lokasi user (misal di Alun-Alun Lembang)
    user_lat, user_lon = -6.8169, 107.6186
    print(f"\nLokasi User (Alun-Alun Lembang): {user_lat}, {user_lon}")

    # 1. Cari TPS terdekat secara jarak lurus
    closest_tps = None
    min_dist = float('inf')
    for tps in tps_list:
        dist = haversine_distance(user_lat, user_lon, tps["lat"], tps["lon"])
        if dist < min_dist:
            min_dist = dist
            closest_tps = tps

    print(f"TPS terdekat terdeteksi: {closest_tps['name']} dengan jarak lurus ~{min_dist:.2f} meter.")

    print("\n--- [3] Mengunduh/Memuat Peta Jalan raya menggunakan OSMnx ---")
    import osmnx as ox
    
    # Gunakan cache file untuk mempercepat running berikutnya
    map_file = "lembang_walk.graphml"
    
    if os.path.exists(map_file):
        print(f"Memuat peta dari file cache lokal '{map_file}'...")
        graph = ox.load_graphml(map_file)
    else:
        print("Mengunduh jaringan jalan dengan radius 3 km dari Alun-Alun Lembang...")
        # Ambil jalan tipe pedestrian/pedestrian-friendly agar akurat untuk pejalan kaki
        graph = ox.graph_from_point((user_lat, user_lon), dist=3000, network_type="walk")
        print(f"Menyimpan cache peta ke '{map_file}'...")
        ox.save_graphml(graph, map_file)

    print(f"Graph Peta berhasil dimuat. Total node: {len(graph.nodes)}, Total edge: {len(graph.edges)}")

    print("\n--- [4] Memetakan Titik Koordinat ke Node Peta Jalan ---")
    # Cari node jalan terdekat di graph dari lokasi user dan lokasi TPS terdekat
    start_node = ox.nearest_nodes(graph, X=user_lon, Y=user_lat)
    goal_node = ox.nearest_nodes(graph, X=closest_tps["lon"], Y=closest_tps["lat"])
    
    print(f"Node awal (User) terdekat di graph: {start_node}")
    print(f"Node tujuan (TPS) terdekat di graph: {goal_node}")

    print("\n--- [5] Menjalankan Algoritma A* Search Kustom ---")
    path_nodes, total_distance = custom_astar_search(graph, start_node, goal_node)
    
    if path_nodes:
        print("[SUCCESS] RUTE DITEMUKAN!")
        print(f"Total Jarak Navigasi Jalan: {total_distance:.2f} meter")
        print(f"Jumlah Node Jalan yang Dilewati: {len(path_nodes)}")
        
        # Cetak beberapa koordinat rute jalan
        print("Daftar koordinat rute jalan (5 node pertama):")
        for i, node_id in enumerate(path_nodes[:5]):
            node_data = graph.nodes[node_id]
            print(f"  Node {i+1}: ({node_data['y']}, {node_data['x']})")
        if len(path_nodes) > 5:
            print(f"  ... dan {len(path_nodes) - 5} node lainnya.")
    else:
        print("[FAILED] Gagal mencari rute menggunakan A* Search.")

if __name__ == "__main__":
    db_conn = setup_database()
    if db_conn:
        try:
            run_routing_test(db_conn)
        finally:
            db_conn.close()
            print("\nKoneksi database ditutup. Pengujian selesai.")
