'use client';

import dynamic from 'next/dynamic';
import { StripedSurface } from '@/app/_components/ui/striped-surface';

export const RouteMap = dynamic(
  () => import('./route-map').then((module) => module.RouteMap),
  {
    ssr: false,
    loading: () => (
      <StripedSurface caption="Memuat peta…" style={{ height: '100%' }} />
    ),
  }
);
