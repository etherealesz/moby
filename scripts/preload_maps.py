import os
import osmnx as ox

# Konfigurasi caching dan timeout OSMnx
ox.settings.timeout = 180  # Naikkan timeout download ke 3 menit (default 180s)
ox.settings.requests_timeout = 180

# Daftar area koordinat penting untuk demo Skripsi Anda
# Format: (name, start_lat, start_lon, end_lat, end_lon, mode)
DEMO_AREAS = [
    # 1. Rute Jakarta (Monas - Bundaran HI)
    ("Jakarta_Monas_HI_Walk", -6.1754, 106.8272, -6.1950, 106.8229, "walk"),
    ("Jakarta_Monas_HI_Drive", -6.1754, 106.8272, -6.1950, 106.8229, "drive"),
    # 2. Rute Depok (Margonda - Balaikota Depok)
    ("Depok_Margonda_Walk", -6.3731, 106.8346, -6.4025, 106.7942, "walk"),
    ("Depok_Margonda_Drive", -6.3731, 106.8346, -6.4025, 106.7942, "drive"),
    # 3. Rute Kota Tangerang (TangCity - Alun-Alun Tangerang)
    ("Tangerang_TangCity_Walk", -6.1950, 106.6385, -6.1783, 106.6319, "walk"),
    ("Tangerang_TangCity_Drive", -6.1950, 106.6385, -6.1783, 106.6319, "drive"),
    # 4. Rute Kota Bekasi (Summarecon Bekasi - Alun-Alun Bekasi)
    ("Bekasi_Summarecon_Walk", -6.2255, 106.9998, -6.2422, 106.9989, "walk"),
    ("Bekasi_Summarecon_Drive", -6.2255, 106.9998, -6.2422, 106.9989, "drive"),
    # 5. Rute Lembang (Alun-Alun Lembang - Hotel Pesona Bambu)
    ("Lembang_Alun_PesonaBambu_Walk", -6.8169, 107.6186, -6.8122, 107.6158, "walk"),
    ("Lembang_Alun_PesonaBambu_Drive", -6.8169, 107.6186, -6.8122, 107.6158, "drive"),
    # 6. Dusun Bambu TPS Area
    ("Lembang_DusunBambu_Walk", -6.8169, 107.6186, -6.7973820, 107.5746838, "walk"),
    # 7. Laxmi Resto TPS Area
    ("Lembang_LaxmiResto_Walk", -6.8169, 107.6186, -6.8775000, 107.5717684, "walk"),
]


def preload_maps():
    cache_dir = "maps_cache"
    os.makedirs(cache_dir, exist_ok=True)

    print("=== PROGRAM PRE-LOAD PETA JALAN (OSMnx Cache) ===")
    print(
        "Program ini akan mendownload & mengunci peta area demo skripsi Anda agar bisa diakses INSTAN & OFFLINE saat presentasi/sidang.\n"
    )

    padding = 0.005

    for name, start_lat, start_lon, end_lat, end_lon, mode in DEMO_AREAS:
        raw_min_lon = min(start_lon, end_lon) - padding
        raw_min_lat = min(start_lat, end_lat) - padding
        raw_max_lon = max(start_lon, end_lon) + padding
        raw_max_lat = max(start_lat, end_lat) + padding

        min_lon = round(raw_min_lon, 4)
        min_lat = round(raw_min_lat, 4)
        max_lon = round(raw_max_lon, 4)
        max_lat = round(raw_max_lat, 4)

        cache_filename = f"bbox_{min_lon}_{min_lat}_{max_lon}_{max_lat}_{mode}.graphml"
        cache_path = os.path.join(cache_dir, cache_filename)

        if os.path.exists(cache_path):
            print(f"[SUDAH ADA] {name} -> Peta sudah ada di cache lokal. Lewati.")
        else:
            print(
                f"[DOWNLOADING] {name} -> Menghubungi OSM Overpass untuk bbox ({min_lon}, {min_lat}, {max_lon}, {max_lat}) | Mode: {mode}..."
            )
            try:
                bbox_tuple = (min_lon, min_lat, max_lon, max_lat)
                graph = ox.graph_from_bbox(bbox=bbox_tuple, network_type=mode)
                ox.save_graphml(graph, cache_path)
                print(f"  -> SUCCESS! Disimpan ke: {cache_path}\n")
            except Exception as e:
                print(
                    f"  -> FAILED! Gagal mendownload karena server Overpass sibuk: {e}\n"
                )
                print("  Silakan jalankan kembali script ini beberapa menit lagi.")


if __name__ == "__main__":
    preload_maps()
