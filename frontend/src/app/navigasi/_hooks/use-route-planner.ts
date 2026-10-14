'use client';

import { useMemo, useState } from 'react';
import {
  buildDummyRoute,
  getFacilitiesForCategory,
  sortByDistance,
} from '@/app/_data/dummy-route';
import { DUMMY_USER_POSITION } from '@/app/_data/facilities';
import type {
  CategoryName,
  IRouteResult,
  LatLon,
  NetworkType,
} from '@/app/_models/moby';

const MY_LOCATION_LABEL = 'Lokasi Anda saat ini';

export interface IRoutePlannerOptions {
  initialCategory: CategoryName;
  initialFacilityId: number | null;
}

export function useRoutePlanner({
  initialCategory,
  initialFacilityId,
}: IRoutePlannerOptions) {
  const [category, setCategory] = useState(initialCategory);
  const [start, setStart] = useState<LatLon>(DUMMY_USER_POSITION);
  const [startLabel, setStartLabel] = useState(MY_LOCATION_LABEL);
  const [pickOnMap, setPickOnMap] = useState(false);
  const [network, setNetwork] = useState<NetworkType>('walk');
  const [facilityId, setFacilityId] = useState(initialFacilityId);
  const [mobileStep, setMobileStep] = useState<'form' | 'map'>('form');

  const facilities = useMemo(
    () => sortByDistance(getFacilitiesForCategory(category), start),
    [category, start]
  );
  const facility =
    facilities.find((item) => item.id === facilityId) ?? facilities[0] ?? null;

  const [route, setRoute] = useState<IRouteResult | null>(() =>
    facility ? buildDummyRoute(start, facility, network) : null
  );

  const resetRoute = () => setRoute(null);

  return {
    category,
    setCategory: (value: CategoryName) => {
      setCategory(value);
      setFacilityId(null);
      resetRoute();
    },
    facilities,
    facility,
    selectFacility: (id: number) => {
      setFacilityId(id);
      resetRoute();
    },
    start,
    startLabel,
    applyMyLocation: () => {
      setStart(DUMMY_USER_POSITION);
      setStartLabel(MY_LOCATION_LABEL);
      setPickOnMap(false);
      resetRoute();
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
      setStart([lat, lon]);
      setStartLabel(`Titik peta ${lat.toFixed(5)}, ${lon.toFixed(5)}`);
      setPickOnMap(false);
      resetRoute();
    },
    network,
    setNetwork: (value: NetworkType) => {
      setNetwork(value);
      resetRoute();
    },
    route,
    calculate: () => {
      if (!facility) {
        return;
      }
      setRoute(buildDummyRoute(start, facility, network));
      setMobileStep('map');
    },
    mobileStep,
    setMobileStep,
  };
}

export type RoutePlanner = ReturnType<typeof useRoutePlanner>;
