import type { CategoryName, IRouteResult } from '@/app/_models/moby';

export function buildRouteHref(category: CategoryName, route: IRouteResult) {
  const params = new URLSearchParams({
    kategori: category,
    fasilitas: String(route.facility.id),
  });
  return `/navigasi?${params.toString()}`;
}
