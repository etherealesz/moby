'use client';

import { useEffect, useRef } from 'react';
import L from 'leaflet';
import {
  MapContainer,
  Marker,
  Polyline,
  Popup,
  TileLayer,
  useMap,
  useMapEvents,
} from 'react-leaflet';
import { PRIMARY, SEMANTIC, TERTIARY } from '@/lib/constants/colors';

import 'leaflet/dist/leaflet.css';

// ── Custom Pin Icons ────────────────────────────────────────────────────────
const makePin = (color: string, label: string) =>
  L.divIcon({
    html: `<div style="
      width: 24px; height: 24px; border-radius: 50%;
      background: ${color};
      border: 3px solid #ffffff;
      box-shadow: 0 2px 8px rgba(0,0,0,0.35);
      display: flex; align-items: center; justify-content: center;
      color: #ffffff; font-size: 11px; font-weight: 700;
    ">${label}</div>`,
    className: '',
    iconSize: [24, 24],
    iconAnchor: [12, 12],
  });

const startIcon = makePin(PRIMARY[500], 'A');
const endIcon = makePin(SEMANTIC.danger, 'B');

// ── Resizer Component ───────────────────────────────────────────────────────
function MapResizer() {
  const map = useMap();

  useEffect(() => {
    map.invalidateSize();
    const t1 = setTimeout(() => map.invalidateSize(), 150);
    const t2 = setTimeout(() => map.invalidateSize(), 500);

    const container = map.getContainer();
    let resizeObserver: ResizeObserver | null = null;
    if (typeof ResizeObserver !== 'undefined' && container) {
      resizeObserver = new ResizeObserver(() => {
        map.invalidateSize();
      });
      resizeObserver.observe(container);
    }

    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
      if (resizeObserver) {
        resizeObserver.disconnect();
      }
    };
  }, [map]);

  return null;
}

// ── Click Handler ──────────────────────────────────────────────────────────
function MapClickHandler({
  onMapClick,
}: {
  onMapClick?: (lat: number, lon: number) => void;
}) {
  useMapEvents({
    click(e) {
      onMapClick?.(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
}

// ── Smooth Bounding Box Fit (A to B / Route Frame) ─────────────────────────
function FitMapView({
  startCoords,
  endCoords,
  routeCoords,
}: {
  startCoords?: [number, number] | null;
  endCoords?: [number, number] | null;
  routeCoords?: [number, number][] | null;
}) {
  const map = useMap();
  const prevRouteRef = useRef<string | null>(null);
  const prevPointsRef = useRef<string | null>(null);

  useEffect(() => {
    // 1. Jika rute sudah dihitung: fit batas seluruh rute dengan padding lega
    if (routeCoords && routeCoords.length > 1) {
      const routeKey = JSON.stringify(routeCoords[0]) + routeCoords.length;
      if (routeKey !== prevRouteRef.current) {
        prevRouteRef.current = routeKey;
        const bounds = L.latLngBounds(routeCoords);
        map.fitBounds(bounds, {
          padding: [50, 50],
          maxZoom: 16,
          animate: true,
        });
      }
      return;
    }

    // 2. Jika Titik A dan Titik B sudah terpasang: fit bounding box mencakup A dan B (kotakan A ke B)
    if (startCoords && endCoords) {
      const isDifferent =
        Math.abs(startCoords[0] - endCoords[0]) > 0.0001 ||
        Math.abs(startCoords[1] - endCoords[1]) > 0.0001;

      if (isDifferent) {
        const pointsKey = `${startCoords[0]},${startCoords[1]}-${endCoords[0]},${endCoords[1]}`;
        if (pointsKey !== prevPointsRef.current) {
          prevPointsRef.current = pointsKey;
          const bounds = L.latLngBounds([startCoords, endCoords]);
          map.fitBounds(bounds, {
            padding: [60, 60],
            maxZoom: 16,
            animate: true,
          });
        }
        return;
      }
    }

    // 3. Jika baru titik A yang tersedia: center ke A secara halus saat pertama kali dipasang
    if (startCoords && !prevPointsRef.current) {
      prevPointsRef.current = `${startCoords[0]},${startCoords[1]}`;
      map.setView(startCoords, 14, { animate: true });
    }
  }, [startCoords, endCoords, routeCoords, map]);

  return null;
}

// ── Props ──────────────────────────────────────────────────────────────────
interface IMapProps {
  startCoords?: [number, number] | null;
  endCoords?: [number, number] | null;
  routeCoords?: [number, number][] | null;
  mode?: string;
  onMapClick?: (lat: number, lon: number) => void;
}

// ── Main Map Component ─────────────────────────────────────────────────────
export default function Map({
  startCoords,
  endCoords,
  routeCoords,
  mode = 'walk',
  onMapClick,
}: IMapProps) {
  // Default center fallback
  const initialCenter: [number, number] = startCoords || [-6.2088, 106.8456];
  const routeColor = mode === 'walk' ? PRIMARY[500] : TERTIARY[500];

  return (
    <div
      style={{
        width: '100%',
        height: '100%',
        position: 'relative',
        borderRadius: 12,
        overflow: 'hidden',
        border: '1px solid #dbeceb',
        boxShadow: '0 4px 18px rgba(2, 109, 119, 0.08)',
        zIndex: 1,
      }}
    >
      <MapContainer
        center={initialCenter}
        zoom={14}
        zoomControl
        style={{ width: '100%', height: '100%' }}
      >
        {/* Light OSM base tiles */}
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          maxZoom={19}
        />

        <MapResizer />
        <FitMapView
          startCoords={startCoords}
          endCoords={endCoords}
          routeCoords={routeCoords}
        />
        <MapClickHandler onMapClick={onMapClick} />

        {/* Start marker (A) */}
        {startCoords && (
          <Marker position={startCoords} icon={startIcon}>
            <Popup>
              <strong>Titik Awal (A)</strong>
              <br />
              {startCoords[0].toFixed(6)}, {startCoords[1].toFixed(6)}
            </Popup>
          </Marker>
        )}

        {/* End marker (B) */}
        {endCoords && (
          <Marker position={endCoords} icon={endIcon}>
            <Popup>
              <strong>Titik Tujuan (B)</strong>
              <br />
              {endCoords[0].toFixed(6)}, {endCoords[1].toFixed(6)}
            </Popup>
          </Marker>
        )}

        {/* Route polyline */}
        {routeCoords && routeCoords.length > 1 && (
          <Polyline
            positions={routeCoords}
            color={routeColor}
            weight={6}
            opacity={0.9}
            lineJoin="round"
            lineCap="round"
          />
        )}
      </MapContainer>
    </div>
  );
}
