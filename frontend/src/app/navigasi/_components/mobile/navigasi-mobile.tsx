import type { RoutePlanner } from '../../_hooks/use-route-planner';
import { RouteMapScreen } from './route-map-screen';
import { RouteSetupScreen } from './route-setup-screen';

export function NavigasiMobile({ planner }: { planner: RoutePlanner }) {
  return planner.mobileStep === 'map' ? (
    <RouteMapScreen planner={planner} />
  ) : (
    <RouteSetupScreen planner={planner} />
  );
}
