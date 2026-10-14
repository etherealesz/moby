'use client';

import { useEffect } from 'react';
import clsx from 'clsx';
import L from 'leaflet';
import { LuMinus, LuPlus } from 'react-icons/lu';
import {
  MapContainer,
  Marker,
  Polyline,
  TileLayer,
  useMap,
  useMapEvents,
} from 'react-leaflet';
import type { LatLon } from '@/app/_models/moby';
import classes from './route-map.module.css';

import 'leaflet/dist/leaflet.css';

const ROUTE_COLOR = '#276b3f';

const makeIcon = (label: string, className: string) =>
  L.divIcon({
    html: label,
    className: clsx(classes.marker, className),
    iconSize: [36, 36],
    iconAnchor: [18, 18],
  });

const START_ICON = makeIcon('A', classes.markerStart);
const END_ICON = makeIcon('B', classes.markerEnd);

export interface IRouteMapProps {
  start: LatLon;
  end: LatLon | null;
  path: LatLon[] | null;
  pickOnMap?: boolean;
  onMapClick?: (lat: number, lon: number) => void;
  showLegend?: boolean;
  showControls?: boolean;
}

function FitView({
  start,
  end,
  path,
}: Pick<IRouteMapProps, 'start' | 'end' | 'path'>) {
  const map = useMap();

  useEffect(() => {
    const points = path && path.length > 1 ? path : end ? [start, end] : null;
    if (points) {
      map.fitBounds(L.latLngBounds(points), { padding: [72, 72], maxZoom: 17 });
    } else {
      map.setView(start, 15);
    }
  }, [map, start, end, path]);

  useEffect(() => {
    const observer = new ResizeObserver(() => map.invalidateSize());
    observer.observe(map.getContainer());
    return () => observer.disconnect();
  }, [map]);

  return null;
}

function ClickHandler({ onMapClick }: Pick<IRouteMapProps, 'onMapClick'>) {
  useMapEvents({
    click: (event) => onMapClick?.(event.latlng.lat, event.latlng.lng),
  });
  return null;
}

function Controls({ start }: { start: LatLon }) {
  const map = useMap();

  return (
    <div className={classes.controls}>
      <button
        type="button"
        className={classes.control}
        onClick={() => map.zoomIn()}
        aria-label="Perbesar"
      >
        <LuPlus size={18} />
      </button>
      <button
        type="button"
        className={classes.control}
        onClick={() => map.zoomOut()}
        aria-label="Perkecil"
      >
        <LuMinus size={18} />
      </button>
      <button
        type="button"
        className={classes.control}
        onClick={() => map.setView(start, 16)}
        aria-label="Ke posisi saya"
      >
        GPS
      </button>
    </div>
  );
}

function Legend() {
  return (
    <div className={classes.legend}>
      <span className={classes.legendTitle}>Keterangan</span>
      <span className={classes.legendRow}>
        <span className={classes.legendLine} /> Rute A* terpilih
      </span>
      <span className={classes.legendRow}>
        <span className={clsx(classes.legendLine, classes.legendLineMuted)} />{' '}
        Jalan
      </span>
      <span className={classes.legendRow}>
        <span className={classes.legendSquare} /> Fasilitas pengolahan
      </span>
    </div>
  );
}

export function RouteMap({
  start,
  end,
  path,
  pickOnMap = false,
  onMapClick,
  showLegend = false,
  showControls = true,
}: IRouteMapProps) {
  return (
    <div className={clsx(classes.wrapper, pickOnMap && classes.picking)}>
      <MapContainer
        center={start}
        zoom={15}
        zoomControl={false}
        style={{ width: '100%', height: '100%' }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='Data jalan: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> · graf oleh OSMnx'
          maxZoom={19}
        />
        <FitView start={start} end={end} path={path} />
        <ClickHandler onMapClick={onMapClick} />
        {showControls && <Controls start={start} />}

        {path && path.length > 1 && (
          <Polyline
            positions={path}
            pathOptions={{
              color: ROUTE_COLOR,
              weight: 7,
              opacity: 1,
              lineJoin: 'miter',
              lineCap: 'square',
            }}
          />
        )}
        <Marker position={start} icon={START_ICON} />
        {end && <Marker position={end} icon={END_ICON} />}
      </MapContainer>

      {showLegend && <Legend />}
      {pickOnMap && (
        <span className={classes.pickHint}>Klik peta untuk titik awal</span>
      )}
    </div>
  );
}
