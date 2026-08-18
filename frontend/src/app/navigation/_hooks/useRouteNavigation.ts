'use client';

import { useEffect, useState } from 'react';
import useSWRMutation from 'swr/mutation';
import { IRouteRequest } from '../_models/route';
import {
  DEFAULT_JAKARTA_COORDS,
  getCurrentLocation,
} from '../_services/getLocation';
import { getRoute } from '../_services/getRoute';

export const NAVIGATION_ROUTE_SWR_KEY = 'navigation/route';

export function useRouteNavigation() {
  const [startLat, setStartLat] = useState('');
  const [startLon, setStartLon] = useState('');
  const [endLat, setEndLat] = useState('');
  const [endLon, setEndLon] = useState('');
  const [mode, setMode] = useState<'walk' | 'drive'>('walk');
  const [clickAction, setClickAction] = useState<'start' | 'end'>('start');

  const [currentStart, setCurrentStart] = useState<[number, number] | null>([
    DEFAULT_JAKARTA_COORDS.latitude,
    DEFAULT_JAKARTA_COORDS.longitude,
  ]);
  const [currentEnd, setCurrentEnd] = useState<[number, number] | null>(null);
  const [routeCoords, setRouteCoords] = useState<[number, number][] | null>(
    null
  );
  const [gpsLoading, setGpsLoading] = useState(false);
  const [customError, setCustomError] = useState<string | null>(null);

  // SWR Mutation for Route Calculation
  const {
    trigger: fetchRoute,
    isMutating: isRouteLoading,
    error: routeMutationError,
    data: routeResult,
    reset: resetRouteMutation,
  } = useSWRMutation(
    NAVIGATION_ROUTE_SWR_KEY,
    async (_key: string, { arg }: { arg: IRouteRequest }) => {
      return getRoute(arg);
    }
  );

  // Auto-detect GPS on initial mount
  useEffect(() => {
    setGpsLoading(true);
    getCurrentLocation()
      .then((coords) => {
        setStartLat(coords.latitude.toFixed(6));
        setStartLon(coords.longitude.toFixed(6));
        setCurrentStart([coords.latitude, coords.longitude]);
      })
      .catch(() => {
        setStartLat(String(DEFAULT_JAKARTA_COORDS.latitude));
        setStartLon(String(DEFAULT_JAKARTA_COORDS.longitude));
        setCurrentStart([
          DEFAULT_JAKARTA_COORDS.latitude,
          DEFAULT_JAKARTA_COORDS.longitude,
        ]);
      })
      .finally(() => {
        setGpsLoading(false);
      });
  }, []);

  // Sync text inputs to currentStart coordinate pair
  const handleUpdateStartLat = (val: string) => {
    setStartLat(val);
    const lat = parseFloat(val);
    const lon = parseFloat(startLon);
    if (!isNaN(lat) && !isNaN(lon)) {
      setCurrentStart([lat, lon]);
    }
  };

  const handleUpdateStartLon = (val: string) => {
    setStartLon(val);
    const lat = parseFloat(startLat);
    const lon = parseFloat(val);
    if (!isNaN(lat) && !isNaN(lon)) {
      setCurrentStart([lat, lon]);
    }
  };

  // Sync text inputs to currentEnd coordinate pair
  const handleUpdateEndLat = (val: string) => {
    setEndLat(val);
    const lat = parseFloat(val);
    const lon = parseFloat(endLon);
    if (!isNaN(lat) && !isNaN(lon)) {
      setCurrentEnd([lat, lon]);
    }
  };

  const handleUpdateEndLon = (val: string) => {
    setEndLon(val);
    const lat = parseFloat(endLat);
    const lon = parseFloat(val);
    if (!isNaN(lat) && !isNaN(lon)) {
      setCurrentEnd([lat, lon]);
    }
  };

  const handleRefreshGps = () => {
    setGpsLoading(true);
    setCustomError(null);
    getCurrentLocation()
      .then((coords) => {
        setStartLat(coords.latitude.toFixed(6));
        setStartLon(coords.longitude.toFixed(6));
        setCurrentStart([coords.latitude, coords.longitude]);
      })
      .catch((err: Error) => {
        setCustomError(err.message || 'Gagal mendeteksi lokasi GPS.');
      })
      .finally(() => {
        setGpsLoading(false);
      });
  };

  const handleMapClick = (lat: number, lon: number) => {
    if (clickAction === 'start') {
      setStartLat(lat.toFixed(6));
      setStartLon(lon.toFixed(6));
      setCurrentStart([lat, lon]);
    } else {
      setEndLat(lat.toFixed(6));
      setEndLon(lon.toFixed(6));
      setCurrentEnd([lat, lon]);
    }
  };

  const handleCalculateRoute = async (e: React.FormEvent) => {
    e.preventDefault();
    setCustomError(null);

    const sLat = parseFloat(startLat);
    const sLon = parseFloat(startLon);
    const eLat = parseFloat(endLat);
    const eLon = parseFloat(endLon);

    if ([sLat, sLon, eLat, eLon].some(isNaN)) {
      setCustomError('Koordinat harus berupa angka desimal yang valid.');
      return;
    }

    setCurrentStart([sLat, sLon]);
    setCurrentEnd([eLat, eLon]);

    try {
      const res = await fetchRoute({
        start_lat: sLat,
        start_lon: sLon,
        end_lat: eLat,
        end_lon: eLon,
        mode,
      });

      if (res && res.route) {
        setRouteCoords(res.route);
      }
    } catch (err: any) {
      setCustomError(
        err?.response?.data?.detail ||
          err?.message ||
          'Gagal menghitung rute navigasi.'
      );
    }
  };

  const handleReset = () => {
    setRouteCoords(null);
    setCustomError(null);
    resetRouteMutation();
  };

  const errorMessage =
    customError || (routeMutationError ? routeMutationError.message : null);

  return {
    // Form & Coords
    startLat,
    setStartLat: handleUpdateStartLat,
    startLon,
    setStartLon: handleUpdateStartLon,
    endLat,
    setEndLat: handleUpdateEndLat,
    endLon,
    setEndLon: handleUpdateEndLon,
    mode,
    setMode,
    clickAction,
    setClickAction,

    // Map States
    currentStart,
    currentEnd,
    routeCoords,

    // Actions & Handlers
    handleRefreshGps,
    handleMapClick,
    handleCalculateRoute,
    handleReset,

    // Status
    gpsLoading,
    isRouteLoading,
    errorMessage,
    routeResult,
  };
}
