import { notifications } from '@mantine/notifications';
import type { IFacility } from '@/app/_models/moby';

export function showFacilityDetail(facility: IFacility) {
  notifications.show({
    title: facility.name,
    message: `${facility.type} · ${facility.address}, ${facility.city} · buka ${facility.openHours}`,
  });
}

export function startNavigation() {
  notifications.show({
    message: 'Mode navigasi langkah demi langkah belum tersedia (data dummy).',
  });
}
