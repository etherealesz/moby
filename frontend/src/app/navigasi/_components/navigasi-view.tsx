'use client';

import { useIsDesktop } from '@/app/_components/ui/use-is-desktop';
import {
  useRoutePlanner,
  type IRoutePlannerOptions,
} from '../_hooks/use-route-planner';
import { NavigasiDesktop } from './desktop/navigasi-desktop';
import { NavigasiMobile } from './mobile/navigasi-mobile';

interface INavigasiViewProps extends IRoutePlannerOptions {
  initialDesktop: boolean;
}

export function NavigasiView({
  initialDesktop,
  ...options
}: INavigasiViewProps) {
  const isDesktop = useIsDesktop(initialDesktop);
  const planner = useRoutePlanner(options);

  return isDesktop ? (
    <NavigasiDesktop planner={planner} />
  ) : (
    <NavigasiMobile planner={planner} />
  );
}
