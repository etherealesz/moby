import { DesktopFooter } from '@/app/_components/layout/desktop-footer';
import { DesktopHeader } from '@/app/_components/layout/desktop-header';
import { PageFrame } from '@/app/_components/layout/page-frame';
import type { RoutePlanner } from '../../_hooks/use-route-planner';
import { RouteMap } from '../map/route-map-lazy';
import { RoutePlannerForm } from '../shared/route-planner-form';
import { RouteStats } from '../shared/route-stats';
import { FacilityBar } from './facility-bar';
import classes from './desktop.module.css';

export function NavigasiDesktop({ planner }: { planner: RoutePlanner }) {
  const { facility, route } = planner;

  return (
    <PageFrame
      header={<DesktopHeader active="/navigasi" subtitle="Navigasi rute" />}
      footer={<DesktopFooter />}
    >
      <div className={classes.body}>
        <aside className={classes.sidebar}>
          <RoutePlannerForm planner={planner} />
          <div className={classes.sidebarStats}>
            <RouteStats route={route} />
          </div>
        </aside>

        <section className={classes.mapArea} aria-label="Peta rute">
          <div className={classes.mapFill}>
            <RouteMap
              start={planner.start}
              end={facility?.position ?? null}
              path={route?.path ?? null}
              pickOnMap={planner.pickOnMap}
              onMapClick={planner.handleMapClick}
              showLegend
            />
          </div>
          {facility && <FacilityBar facility={facility} />}
        </section>
      </div>
    </PageFrame>
  );
}
