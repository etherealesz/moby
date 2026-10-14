import type {
  CategoryName,
  IFacility,
  IRouteResult,
  LatLon,
  NetworkType,
} from '@/app/_models/moby';
import { etaMinutes, haversineMeter, pathLengthMeter } from '@/app/_utils/geo';
import { getCategory } from './categories';
import { DUMMY_FACILITIES } from './facilities';

function buildStairPath([lat1, lon1]: LatLon, [lat2, lon2]: LatLon): LatLon[] {
  const midLat = lat1 + (lat2 - lat1) * 0.35;
  const midLon = lon1 + (lon2 - lon1) * 0.45;
  return [
    [lat1, lon1],
    [midLat, lon1],
    [midLat, midLon],
    [lat2, midLon],
    [lat2, lon2],
  ];
}

export function getFacilitiesForCategory(category: CategoryName): IFacility[] {
  const { facilityTypes } = getCategory(category);
  return DUMMY_FACILITIES.filter((facility) =>
    facilityTypes.includes(facility.type)
  );
}

export function sortByDistance(facilities: IFacility[], from: LatLon) {
  return [...facilities].sort(
    (a, b) =>
      haversineMeter(from, a.position) - haversineMeter(from, b.position)
  );
}

export function buildDummyRoute(
  from: LatLon,
  facility: IFacility,
  network: NetworkType
): IRouteResult {
  const path = buildStairPath(from, facility.position);
  const distanceMeter = pathLengthMeter(path);
  return {
    facility,
    path,
    distanceMeter,
    etaMinutes: etaMinutes(distanceMeter, network),
    network,
  };
}

export function findNearestRoute(
  category: CategoryName,
  from: LatLon,
  network: NetworkType = 'walk'
): IRouteResult | null {
  const [nearest] = sortByDistance(getFacilitiesForCategory(category), from);
  return nearest ? buildDummyRoute(from, nearest, network) : null;
}
