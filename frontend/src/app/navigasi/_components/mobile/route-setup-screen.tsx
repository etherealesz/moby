import { MobileTopBar } from '@/app/_components/layout/mobile-top-bar';
import { PageFrame } from '@/app/_components/layout/page-frame';
import type { RoutePlanner } from '../../_hooks/use-route-planner';
import { RoutePlannerForm } from '../shared/route-planner-form';
import { RouteStats } from '../shared/route-stats';
import classes from './mobile.module.css';

export function RouteSetupScreen({ planner }: { planner: RoutePlanner }) {
  return (
    <PageFrame header={<MobileTopBar title="Atur Rute" backHref="/" />}>
      <div className={classes.form}>
        <RoutePlannerForm planner={planner} />
      </div>
      <RouteStats route={planner.route} align="start" />
    </PageFrame>
  );
}
