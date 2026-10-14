import { Stat } from '@/app/_components/ui/stat';
import type { IRouteResult } from '@/app/_models/moby';
import { NETWORK_LABEL, splitDistance } from '@/app/_utils/format';
import classes from './shared.module.css';

interface IRouteStatsProps {
  route: IRouteResult | null;
  align?: 'center' | 'start';
}

export function RouteStats({ route, align = 'center' }: IRouteStatsProps) {
  const distance = route ? splitDistance(route.distanceMeter) : null;

  return (
    <div className={classes.stats}>
      <Stat
        value={distance?.value ?? '—'}
        unit={distance?.unit}
        label="Jarak"
        align={align}
      />
      <Stat
        value={route?.etaMinutes ?? '—'}
        unit={route ? 'menit' : undefined}
        label={
          route ? `Estimasi · ${NETWORK_LABEL[route.network]}` : 'Estimasi'
        }
        align={align}
      />
    </div>
  );
}
