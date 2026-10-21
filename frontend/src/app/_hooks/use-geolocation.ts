'use client';

import { useCallback, useEffect, useState } from 'react';
import type { LatLon } from '@/app/_models/moby';

export interface IGeoFix {
  position: LatLon;
  accuracyMeter: number;
}

function describeGeoError(error: GeolocationPositionError | null) {
  if (!error) {
    return 'Browser tidak mendukung GPS.';
  }
  if (error.code === error.PERMISSION_DENIED) {
    return 'Izin lokasi ditolak. Izinkan lokasi atau pilih titik di peta.';
  }
  if (error.code === error.TIMEOUT) {
    return 'GPS tidak merespons. Coba lagi atau pilih titik di peta.';
  }
  return 'Lokasi tidak tersedia. Pilih titik di peta.';
}

function parseMockFix(): IGeoFix | null {
  const [lat, lon] = (process.env.NEXT_PUBLIC_MOCK_LOCATION ?? '')
    .split(',')
    .map(Number);
  if (!Number.isFinite(lat) || !Number.isFinite(lon)) {
    return null;
  }
  return { position: [lat, lon], accuracyMeter: 0 };
}

const MOCK_FIX = parseMockFix();

export function useGeolocation(enabled = true) {
  const [fix, setFix] = useState<IGeoFix | null>(MOCK_FIX);
  const [error, setError] = useState<string | null>(null);
  const [locating, setLocating] = useState(false);

  const locate = useCallback(() => {
    if (MOCK_FIX) {
      setFix(MOCK_FIX);
      return;
    }
    if (!navigator.geolocation) {
      setError(describeGeoError(null));
      return;
    }
    setLocating(true);
    navigator.geolocation.getCurrentPosition(
      ({ coords }) => {
        setFix({
          position: [coords.latitude, coords.longitude],
          accuracyMeter: coords.accuracy,
        });
        setError(null);
        setLocating(false);
      },
      (cause) => {
        setError(describeGeoError(cause));
        setLocating(false);
      },
      { enableHighAccuracy: true, timeout: 10_000, maximumAge: 30_000 }
    );
  }, []);

  useEffect(() => {
    if (enabled && !fix) {
      const timer = setTimeout(locate, 0);
      return () => clearTimeout(timer);
    }
    return undefined;
  }, [enabled, fix, locate]);

  return { fix, error, locating, locate };
}
