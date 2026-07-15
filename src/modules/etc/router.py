from typing import List
from fastapi import APIRouter, status
from fastapi.responses import HTMLResponse

from app.schemas.response import SStandardResponse
from app.utils.standard_response_builder import StandardResponseBuilder

tags: List = ["API / Etc"]
router = APIRouter(tags=tags)


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> SStandardResponse:
    return StandardResponseBuilder().build()


@router.get("/demo", response_class=HTMLResponse)
async def get_demo_page():
    html_content = """<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>A* Search Navigation Demo - Skripsi</title>
    
    <!-- Google Fonts - Inter & Outfit -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet">
    
    <!-- Leaflet.js CSS -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin=""/>
    
    <style>
        :root {
            --bg-dark: #0f172a;
            --card-dark: rgba(30, 41, 59, 0.7);
            --primary: #3b82f6;
            --primary-hover: #2563eb;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --border: rgba(255, 255, 255, 0.08);
            --font-outfit: 'Outfit', sans-serif;
            --font-inter: 'Inter', sans-serif;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: var(--font-inter);
            background-color: var(--bg-dark);
            color: var(--text-main);
            height: 100vh;
            display: flex;
            overflow: hidden;
        }

        /* Sidebar Glassmorphism */
        .sidebar {
            width: 420px;
            background: var(--card-dark);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-right: 1px solid var(--border);
            padding: 2.5rem;
            display: flex;
            flex-direction: column;
            gap: 2rem;
            z-index: 1000;
            box-shadow: 10px 0 30px rgba(0, 0, 0, 0.25);
            overflow-y: auto;
        }

        .header h1 {
            font-family: var(--font-outfit);
            font-size: 1.8rem;
            font-weight: 700;
            background: linear-gradient(135deg, #60a5fa, #3b82f6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }

        .header p {
            font-size: 0.875rem;
            color: var(--text-muted);
            line-height: 1.4;
        }

        .form-group {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }

        label {
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
        }

        .coords-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1rem;
        }

        input, select {
            width: 100%;
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid var(--border);
            color: var(--text-main);
            padding: 0.75rem 1rem;
            border-radius: 8px;
            font-family: var(--font-inter);
            font-size: 0.9rem;
            transition: all 0.2s ease;
        }

        input:focus, select:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
        }

        .btn-submit {
            background: linear-gradient(135deg, #3b82f6, #1d4ed8);
            border: none;
            color: white;
            padding: 1rem;
            border-radius: 10px;
            font-family: var(--font-outfit);
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 0.5rem;
        }

        .btn-submit:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
            background: linear-gradient(135deg, #4f46e5, #3b82f6);
        }

        .btn-submit:active {
            transform: translateY(1px);
        }

        /* Result Box */
        .result-box {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.5rem;
            display: none;
            flex-direction: column;
            gap: 0.75rem;
            animation: fadeIn 0.4s ease forwards;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .result-title {
            font-family: var(--font-outfit);
            font-size: 1.1rem;
            font-weight: 600;
            color: #60a5fa;
            border-bottom: 1px solid var(--border);
            padding-bottom: 0.5rem;
            margin-bottom: 0.25rem;
        }

        .result-row {
            display: flex;
            justify-content: space-between;
            font-size: 0.875rem;
        }

        .result-val {
            font-weight: 600;
            color: var(--text-main);
        }

        .result-label {
            color: var(--text-muted);
        }

        /* Main Map Container */
        .map-container {
            flex-grow: 1;
            height: 100%;
            position: relative;
        }

        #map {
            width: 100%;
            height: 100%;
            background-color: #111b27;
        }

        /* Quick presets helper */
        .presets {
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
        }

        .preset-btn {
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid var(--border);
            color: var(--text-muted);
            padding: 0.4rem 0.8rem;
            border-radius: 20px;
            font-size: 0.75rem;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .preset-btn:hover {
            background: rgba(59, 130, 246, 0.1);
            color: #60a5fa;
            border-color: rgba(59, 130, 246, 0.3);
        }

        /* Loader */
        .loader {
            display: none;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            border-top-color: white;
            animation: spin 0.8s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body>

    <div class="sidebar">
        <div class="header">
            <h1>A* Navigation Demo</h1>
            <p>Implementasi Algoritma A* Search dengan Jaringan Jalan OpenStreetMap Nyata (OSMnx)</p>
        </div>

        <div class="presets">
            <button class="preset-btn" onclick="applyPreset(-6.1754, 106.8272, -6.1950, 106.8229, 'Jakarta (Monas - HI)')">Jakarta (Monas - HI)</button>
            <button class="preset-btn" onclick="applyPreset(-6.8169, 107.6186, -6.8122, 107.6158, 'Lembang (Alun-Alun - TPS)')">Lembang (Alun-Alun - TPS)</button>
        </div>

        <form id="routingForm" onsubmit="calculateRoute(event)">
            <div style="display: flex; flex-direction: column; gap: 1.25rem;">
                <div class="form-group">
                    <label>Titik Awal (Start)</label>
                    <div class="coords-grid">
                        <div class="form-group">
                            <label style="font-size: 0.65rem;">Latitude</label>
                            <input type="number" step="any" id="start_lat" value="-6.1754" required>
                        </div>
                        <div class="form-group">
                            <label style="font-size: 0.65rem;">Longitude</label>
                            <input type="number" step="any" id="start_lon" value="106.8272" required>
                        </div>
                    </div>
                </div>

                <div class="form-group">
                    <label>Titik Akhir (Goal)</label>
                    <div class="coords-grid">
                        <div class="form-group">
                            <label style="font-size: 0.65rem;">Latitude</label>
                            <input type="number" step="any" id="end_lat" value="-6.1950" required>
                        </div>
                        <div class="form-group">
                            <label style="font-size: 0.65rem;">Longitude</label>
                            <input type="number" step="any" id="end_lon" value="106.8229" required>
                        </div>
                    </div>
                </div>

                <div class="form-group">
                    <label for="mode">Mode Perjalanan</label>
                    <select id="mode">
                        <option value="walk">Walk (Pejalan Kaki)</option>
                        <option value="drive">Drive (Kendaraan)</option>
                    </select>
                </div>

                <button type="submit" class="btn-submit" id="btnSubmit">
                    <span class="loader" id="btnLoader"></span>
                    <span id="btnText">Cari Rute A*</span>
                </button>
            </div>
        </form>

        <div class="result-box" id="resultBox">
            <div class="result-title">Hasil Analisis Rute</div>
            <div class="result-row">
                <span class="result-label">Jarak Navigasi:</span>
                <span class="result-val" id="resDistance">-</span>
            </div>
            <div class="result-row">
                <span class="result-label">Mode:</span>
                <span class="result-val" id="resMode">-</span>
            </div>
            <div class="result-row">
                <span class="result-label">Node Dilewati:</span>
                <span class="result-val" id="resNodes">-</span>
            </div>
            <div class="result-row">
                <span class="result-label">Algoritma:</span>
                <span class="result-val" style="color: #4ade80;">A* Search (Kustom)</span>
            </div>
        </div>
    </div>

    <div class="map-container">
        <div id="map"></div>
    </div>

    <!-- Leaflet.js JS -->
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
    
    <script>
        // Inisialisasi Peta Leaflet Centered di Jakarta
        const map = L.map('map', {
            zoomControl: false
        }).setView([-6.1850, 106.8250], 14);

        // Tambah Zoom Control di kanan bawah
        L.control.zoom({ position: 'bottomright' }).addTo(map);

        // Pasang Map Tile Dark Mode (CartoDB Dark Matter)
        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
            subdomains: 'abcd',
            maxZoom: 20
        }).addTo(map);

        let startMarker = null;
        let endMarker = null;
        let routeLine = null;

        // Custom Icons
        const startIcon = L.divIcon({
            html: '<div style="background-color: #3b82f6; width: 14px; height: 14px; border-radius: 50%; border: 3px solid white; box-shadow: 0 0 10px rgba(59, 130, 246, 0.8);"></div>',
            className: 'custom-pin-start',
            iconSize: [14, 14],
            iconAnchor: [7, 7]
        });

        const endIcon = L.divIcon({
            html: '<div style="background-color: #ef4444; width: 14px; height: 14px; border-radius: 50%; border: 3px solid white; box-shadow: 0 0 10px rgba(239, 68, 68, 0.8);"></div>',
            className: 'custom-pin-end',
            iconSize: [14, 14],
            iconAnchor: [7, 7]
        });

        function applyPreset(slat, slon, elat, elon, label) {
            document.getElementById('start_lat').value = slat;
            document.getElementById('start_lon').value = slon;
            document.getElementById('end_lat').value = elat;
            document.getElementById('end_lon').value = elon;
            
            // Pan ke area
            map.setView([ (slat+elat)/2, (slon+elon)/2 ], 14);
        }

        async function calculateRoute(event) {
            event.preventDefault();
            
            const startLat = parseFloat(document.getElementById('start_lat').value);
            const startLon = parseFloat(document.getElementById('start_lon').value);
            const endLat = parseFloat(document.getElementById('end_lat').value);
            const endLon = parseFloat(document.getElementById('end_lon').value);
            const mode = document.getElementById('mode').value;

            // Reset marker & line
            if (startMarker) map.removeLayer(startMarker);
            if (endMarker) map.removeLayer(endMarker);
            if (routeLine) map.removeLayer(routeLine);

            // Loader on
            document.getElementById('btnLoader').style.display = 'inline-block';
            document.getElementById('btnText').innerText = 'Menghitung rute...';
            document.getElementById('btnSubmit').disabled = true;
            document.getElementById('resultBox').style.display = 'none';

            // Posisikan Marker Awal & Akhir
            startMarker = L.marker([startLat, startLon], {icon: startIcon}).addTo(map).bindPopup("<b>Titik Awal (Start)</b>");
            endMarker = L.marker([endLat, endLon], {icon: endIcon}).addTo(map).bindPopup("<b>Titik Akhir (Goal)</b>");

            try {
                // Sesuai config URL FastAPI template Anda: /fastapi-template/api/navigation/route
                const prefixUrl = window.location.pathname.replace('/demo', '/api');
                const response = await fetch(`${prefixUrl}/navigation/route`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        start_lat: startLat,
                        start_lon: startLon,
                        end_lat: endLat,
                        end_lon: endLon,
                        mode: mode
                    })
                });

                const resJson = await response.json();
                
                if (!response.ok) {
                    throw new Error(resJson.message || resJson.detail || "Terjadi kesalahan saat memproses rute.");
                }

                const data = resJson.data;
                const routeCoords = data.route; // List of [lat, lon]

                // Tentukan warna garis: Biru untuk jalan kaki, Oranye/Merah untuk berkendara
                const lineColor = (mode === 'walk') ? '#3b82f6' : '#f97316';

                // Gambar Polyline
                routeLine = L.polyline(routeCoords, {
                    color: lineColor,
                    weight: 5,
                    opacity: 0.85,
                    lineJoin: 'round'
                }).addTo(map);

                // Fit bounds ke rute
                map.fitBounds(routeLine.getBounds(), { padding: [50, 50] });

                // Tampilkan Info Analisis
                document.getElementById('resDistance').innerText = `${(data.distance_meters / 1000).toFixed(2)} km (${data.distance_meters} m)`;
                document.getElementById('resMode').innerText = (data.mode === 'walk') ? 'Walk (Pedestrian)' : 'Drive (Road Network)';
                document.getElementById('resNodes').innerText = `${routeCoords.length} Nodes`;
                document.getElementById('resultBox').style.display = 'flex';

            } catch (err) {
                alert(`Error: ${err.message}`);
                console.error(err);
            } finally {
                // Loader off
                document.getElementById('btnLoader').style.display = 'none';
                document.getElementById('btnText').innerText = 'Cari Rute A*';
                document.getElementById('btnSubmit').disabled = false;
            }
        }
    </script>
</body>
</html>
"""
    return HTMLResponse(content=html_content, status_code=200)
