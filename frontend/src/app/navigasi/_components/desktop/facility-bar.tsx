import clsx from 'clsx';
import { buttonClasses } from '@/app/_components/ui/link-button';
import type { IFacility } from '@/app/_models/moby';
import {
  showFacilityDetail,
  startNavigation,
} from '../shared/facility-actions';
import classes from './desktop.module.css';

export function FacilityBar({ facility }: { facility: IFacility }) {
  return (
    <div className={classes.facilityBar}>
      <div>
        <h2 className={classes.facilityName}>{facility.name}</h2>
        <p className={classes.facilityMeta}>
          {[facility.type, facility.address, facility.city]
            .filter(Boolean)
            .join(' · ')}
        </p>
      </div>
      <div className={classes.facilityActions}>
        <button
          type="button"
          onClick={() => showFacilityDetail(facility)}
          className={clsx(
            buttonClasses.base,
            buttonClasses.outline,
            buttonClasses.small
          )}
        >
          Detail fasilitas
        </button>
        <button
          type="button"
          onClick={startNavigation}
          className={clsx(
            buttonClasses.base,
            buttonClasses.primary,
            buttonClasses.small
          )}
        >
          Mulai navigasi
        </button>
      </div>
    </div>
  );
}
