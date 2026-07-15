import math
import heapq

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Fungsi Heuristik h(n): Jarak garis lurus (lingkaran besar bumi) antara dua titik koordinat.
    """
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
    Mencari rute terpendek di atas graph OSMnx menggunakan algoritma A* Search kustom.
    
    Args:
        graph: NetworkX graph dari OSMnx.
        start_node: ID node awal di graph.
        goal_node: ID node tujuan di graph.
        
    Returns:
        tuple: (list of node IDs, total distance in meters)
    """
    open_set = []
    # Simpan di priority queue: (f_score, node_id)
    heapq.heappush(open_set, (0.0, start_node))
    came_from = {}
    
    # g_score: Jarak aktual dari start ke node saat ini
    g_score = {node: float('inf') for node in graph.nodes}
    g_score[start_node] = 0.0
    
    # f_score = g_score + h(n)
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
        
        # Jika sudah sampai di node tujuan
        if current == goal_node:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start_node)
            path.reverse()
            return path, g_score[goal_node]
        
        # Periksa tetangga dari node saat ini
        for neighbor in graph.neighbors(current):
            edge_data = graph.get_edge_data(current, neighbor)
            if edge_data is None:
                continue
            
            # Ambil panjang jalan (length) terpendek jika ada jalan ganda (parallel edges)
            weight = min(edge.get('length', float('inf')) for edge in edge_data.values())
            
            tentative_g_score = g_score[current] + weight
            
            if tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                
                # Hitung heuristik dari tetangga ke target
                neighbor_lat = graph.nodes[neighbor]['y']
                neighbor_lon = graph.nodes[neighbor]['x']
                h_score = haversine_distance(neighbor_lat, neighbor_lon, goal_lat, goal_lon)
                
                f_score[neighbor] = tentative_g_score + h_score
                
                if neighbor not in open_set_hash:
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
                    open_set_hash.add(neighbor)
                    
    return None, float('inf')
