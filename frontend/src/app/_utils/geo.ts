import type { LatLon, NetworkType } from '@/app/_models/moby';

const EARTH_RADIUS_METER = 6_371_000;

const SPEED_KMH: Record<NetworkType, number> = { walk: 4.8, drive: 30 };

const toRad = (deg: number) => (deg * Math.PI) / 180;

/** Jarak Haversine dalam meter (Persamaan 2.45, r = 6.371 km). */
export function haversineMeter([lat1, lon1]: LatLon, [lat2, lon2]: LatLon) {
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) ** 2;
  return 2 * EARTH_RADIUS_METER * Math.asin(Math.sqrt(a));
}

export function pathLengthMeter(path: LatLon[]) {
  let total = 0;
  for (let i = 1; i < path.length; i += 1) {
    total += haversineMeter(path[i - 1], path[i]);
  }
  return total;
}

export function etaMinutes(distanceMeter: number, network: NetworkType) {
  return Math.max(
    1,
    Math.round((distanceMeter / 1000 / SPEED_KMH[network]) * 60)
  );
}
