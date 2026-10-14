import clsx from 'clsx';
import { MobileTopBar } from '@/app/_components/layout/mobile-top-bar';
import { PageFrame } from '@/app/_components/layout/page-frame';
import { buttonClasses } from '@/app/_components/ui/link-button';
import type { RoutePlanner } from '../../_hooks/use-route-planner';
import { RouteMap } from '../map/route-map-lazy';
import { startNavigation } from '../shared/facility-actions';
import { RouteStats } from '../shared/route-stats';
import classes from './mobile.module.css';

const primaryBlock = clsx(
  buttonClasses.base,
  buttonClasses.primary,
  buttonClasses.block
);

export function RouteMapScreen({ planner }: { planner: RoutePlanner }) {
  const { facility, route } = planner;

  return (
    <PageFrame
      header={
        <MobileTopBar
          title="Navigasi Rute"
          onBack={() => planner.setMobileStep('form')}
          actions={
            facility && <span className={classes.city}>{facility.city}</span>
          }
        />
      }
    >
      <div className={classes.map}>
        <RouteMap
          start={planner.start}
          end={facility?.position ?? null}
          path={route?.path ?? null}
          pickOnMap={planner.pickOnMap}
          onMapClick={planner.handleMapClick}
        />
      </div>

      <RouteStats route={route} align="start" />

      {facility && (
        <section className={classes.facility}>
          <h2 className={classes.facilityName}>{facility.name}</h2>
          <p className={classes.facilityMeta}>
            {facility.address} · buka {facility.openHours}
          </p>
          {route ? (
            <button
              type="button"
              className={primaryBlock}
              onClick={startNavigation}
            >
              Mulai navigasi
            </button>
          ) : (
            <button
              type="button"
              className={primaryBlock}
              onClick={planner.calculate}
            >
              Hitung rute A*
            </button>
          )}
        </section>
      )}
    </PageFrame>
  );
}
