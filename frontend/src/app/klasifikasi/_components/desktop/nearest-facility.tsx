import { LinkButton } from '@/app/_components/ui/link-button';
import { MutedLabel } from '@/app/_components/ui/text';
import { formatDistance, NETWORK_LABEL } from '@/app/_utils/format';
import type { ClassificationSession } from '../../_hooks/use-classification-session';
import { buildRouteHref } from '../shared/route-href';
import classes from './desktop.module.css';

type INearestFacilityProps = Pick<
  ClassificationSession,
  'nearestRoute' | 'selected'
>;

export function NearestFacility({
  nearestRoute,
  selected,
}: INearestFacilityProps) {
  if (!nearestRoute || !selected) {
    return null;
  }

  return (
    <section className={classes.facility} aria-label="Fasilitas terdekat">
      <MutedLabel>Fasilitas terdekat</MutedLabel>
      <h2 className={classes.facilityName}>{nearestRoute.facility.name}</h2>
      <p className={classes.facilityMeta}>
        {formatDistance(nearestRoute.distanceMeter)} · kira-kira{' '}
        {nearestRoute.etaMinutes} menit{' '}
        {NETWORK_LABEL[nearestRoute.network].toLowerCase()}
      </p>
      <LinkButton href={buildRouteHref(selected.category, nearestRoute)} block>
        Hitung rute ke fasilitas
      </LinkButton>
    </section>
  );
}
