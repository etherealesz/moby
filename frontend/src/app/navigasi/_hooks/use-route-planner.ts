'use client';

import { useEffect, useState } from 'react';
import { useGeolocation } from '@/app/_hooks/use-geolocation';
import type {
  CategoryName,
  IRouteResult,
  LatLon,
  NetworkType,
} from '@/app/_models/moby';
import {
  describeRouteError,
  fetchRoute,
  type ICandidateRoute,
} from '@/app/_services/route';

export interface IRoutePlannerOptions {
  initialCategory: CategoryName;
  initialFacilityId: number | null;
}

interface IRouteState {
  key: string;
  route: IRouteResult | null;
  candidates: ICandidateRoute[];
  error: string | null;
}

export function useRoutePlanner({
  initialCategory,
  initialFacilityId,
}: IRoutePlannerOptions) {
  const geo = useGeolocation();
  const [category, setCategory] = useState(initialCategory);
  const [mapPoint, setMapPoint] = useState<LatLon | null>(null);
  const [pickOnMap, setPickOnMap] = useState(false);
  const [network, setNetwork] = useState<NetworkType>('walk');
  const [facilityId, setFacilityId] = useState(initialFacilityId);
  const [mobileStep, setMobileStep] = useState<'form' | 'map'>('form');
  const [result, setResult] = useState<IRouteState | null>(null);
  const [nearest, setNearest] = useState<IRouteState | null>(null);
  const [attempt, setAttempt] = useState(0);

  const start = mapPoint ?? geo.fix?.position ?? null;
  const baseKey = start ? `${start.join(',')}|${category}|${network}` : null;
  const key = baseKey ? `${baseKey}|${facilityId ?? 'nearest'}` : null;

  useEffect(() => {
    if (!start || !key || !baseKey) {
      return undefined;
    }
    const controller = new AbortController();
    fetchRoute({ start, category, network, facilityId }, controller.signal)
      .then(({ route, candidates }) => {
        const state = { key, route, candidates, error: null };
        setResult(state);
        if (facilityId === null) {
          setNearest({ ...state, key: baseKey });
        }
      })
      .catch((cause: unknown) => {
        if (!controller.signal.aborted) {
          setResult({
            key,
            route: null,
            candidates: [],
            error: describeRouteError(cause),
          });
        }
      });
    return () => controller.abort();
  }, [key, attempt]);

  const current = result?.key === key ? result : null;
  const loading = !!key && !current;
  const route = current?.route ?? null;
  const candidates = (
    nearest?.key === baseKey ? nearest.candidates : (current?.candidates ?? [])
  ).filter((candidate) => candidate.routeDistanceMeter !== null);
  const facility =
    route?.facility ??
    candidates.find((candidate) => candidate.facility.id === facilityId)
      ?.facility ??
    null;

  const startLabel = mapPoint
    ? `Titik peta ${mapPoint[0].toFixed(5)}, ${mapPoint[1].toFixed(5)}`
    : geo.fix
      ? `Lokasi Anda (akurasi ±${Math.round(geo.fix.accuracyMeter)} m)`
      : geo.locating
        ? 'Mencari lokasi Anda…'
        : 'Lokasi belum tersedia';

  return {
    category,
    setCategory: (value: CategoryName) => {
      setCategory(value);
      setFacilityId(null);
    },
    candidates,
    facility,
    facilityId: facility?.id ?? facilityId,
    selectFacility: (id: number) => setFacilityId(id),
    start,
    startLabel,
    locationError: mapPoint ? null : geo.error,
    locating: geo.locating,
    applyMyLocation: () => {
      setMapPoint(null);
      setFacilityId(null);
      setPickOnMap(false);
      geo.locate();
    },
    pickOnMap,
    togglePickOnMap: () => {
      if (!pickOnMap) {
        setMobileStep('map');
      }
      setPickOnMap(!pickOnMap);
    },
    handleMapClick: (lat: number, lon: number) => {
      if (!pickOnMap) {
        return;
      }
      setMapPoint([lat, lon]);
      setFacilityId(null);
      setPickOnMap(false);
    },
    network,
    setNetwork,
    route,
    loading,
    error: current?.error ?? null,
    calculate: () => {
      if (current?.error) {
        setResult(null);
        setAttempt((value) => value + 1);
      }
      setMobileStep('map');
    },
    mobileStep,
    setMobileStep,
  };
}

export type RoutePlanner = ReturnType<typeof useRoutePlanner>;
