import { isAxiosError } from 'axios';
import type {
  CategoryName,
  FacilityType,
  IFacility,
  IRouteResult,
  LatLon,
  NetworkType,
} from '@/app/_models/moby';
import { etaMinutes } from '@/app/_utils/geo';
import httpClient from '@/lib/api/http/client';
import { ApplicationError } from '@/shared/errors';

interface IFacilityResponse {
  facility_id: number;
  facility_name: string;
  facility_type: FacilityType;
  latitude: number;
  longitude: number;
  address: string | null;
  city: string;
}

interface ICandidateResponse {
  facility: IFacilityResponse;
  straight_distance_meter: number;
  route_distance_meter: number | null;
}

interface IRouteResponse {
  facility: IFacilityResponse;
  network_type: NetworkType;
  route: LatLon[];
  distance_meter: number;
  explored_nodes: number;
  computation_time_ms: number;
  candidates: ICandidateResponse[];
}

export interface ICandidateRoute {
  facility: IFacility;
  straightDistanceMeter: number;
  routeDistanceMeter: number | null;
}

export interface IRouteRequest {
  start: LatLon;
  category: CategoryName;
  network: NetworkType;
  facilityId?: number | null;
}

export interface IRouteResponseData {
  route: IRouteResult;
  candidates: ICandidateRoute[];
}

const ERROR_MESSAGES: Record<string, string> = {
  FACILITY_NOT_FOUND: 'Belum ada fasilitas untuk kategori ini.',
  FACILITY_OUT_OF_RANGE:
    'Tidak ada fasilitas penerima dalam radius pencarian dari titik awal.',
  LOCATION_OUT_OF_COVERAGE:
    'Titik awal terlalu jauh dari jaringan jalan wilayah studi.',
  ROAD_GRAPH_NOT_AVAILABLE: 'Graf jalan belum tersedia untuk area ini.',
  ROUTE_NOT_FOUND: 'Tidak ada rute yang tersambung ke fasilitas terdekat.',
  GET_FACILITY_FAILED: 'Server gagal membaca data fasilitas.',
  GET_ROAD_GRAPH_FAILED: 'Server gagal membaca graf jalan.',
};

function toFacility(item: IFacilityResponse): IFacility {
  return {
    id: item.facility_id,
    name: item.facility_name,
    type: item.facility_type,
    address: item.address ?? '',
    city: item.city,
    position: [item.latitude, item.longitude],
  };
}

export async function fetchRoute(
  { start, category, network, facilityId }: IRouteRequest,
  signal?: AbortSignal
): Promise<IRouteResponseData> {
  const response = await httpClient.trashNav.post<{ data: IRouteResponse }>(
    '/moby/api/route',
    {
      latitude: start[0],
      longitude: start[1],
      category,
      network_type: network,
      facility_id: facilityId ?? null,
    },
    { signal, timeout: 30_000 }
  );
  const data = response.data.data;

  return {
    route: {
      facility: toFacility(data.facility),
      path: data.route,
      distanceMeter: data.distance_meter,
      etaMinutes: etaMinutes(data.distance_meter, data.network_type),
      network: data.network_type,
    },
    candidates: data.candidates.map((candidate) => ({
      facility: toFacility(candidate.facility),
      straightDistanceMeter: candidate.straight_distance_meter,
      routeDistanceMeter: candidate.route_distance_meter,
    })),
  };
}

export function describeRouteError(error: unknown) {
  if (error instanceof ApplicationError) {
    return 'Tidak terhubung ke server.';
  }
  if (isAxiosError(error)) {
    const code = error.response?.data?.error?.message;
    if (typeof code === 'string' && ERROR_MESSAGES[code]) {
      return ERROR_MESSAGES[code];
    }
  }
  return 'Rute gagal dihitung.';
}
