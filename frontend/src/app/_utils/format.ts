import type { NetworkType } from '@/app/_models/moby';

const KM_FORMAT = new Intl.NumberFormat('id-ID', {
  minimumFractionDigits: 1,
  maximumFractionDigits: 1,
});

export function splitDistance(meter: number) {
  if (meter < 1000) {
    return { value: String(Math.round(meter)), unit: 'm' };
  }
  return { value: KM_FORMAT.format(meter / 1000), unit: 'km' };
}

export function formatDistance(meter: number) {
  const { value, unit } = splitDistance(meter);
  return `${value} ${unit}`;
}

export const NETWORK_LABEL: Record<NetworkType, string> = {
  walk: 'Jalan kaki',
  drive: 'Berkendara',
};
