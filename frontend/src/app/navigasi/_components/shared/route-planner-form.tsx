import clsx from 'clsx';
import { buttonClasses } from '@/app/_components/ui/link-button';
import { MutedLabel } from '@/app/_components/ui/text';
import { CATEGORY_NAMES } from '@/app/_models/moby';
import type { RoutePlanner } from '../../_hooks/use-route-planner';
import { ModePicker } from './mode-picker';
import { PillGroup } from './pill-group';
import { RouteEndpoints } from './route-endpoints';
import classes from './shared.module.css';

const CATEGORY_OPTIONS = CATEGORY_NAMES.map((name) => ({
  value: name,
  label: name,
}));

export function RoutePlannerForm({ planner }: { planner: RoutePlanner }) {
  const facilityOptions = planner.facilities.map((facility) => ({
    value: facility.id,
    label: facility.name,
  }));
  const outline = clsx(
    buttonClasses.base,
    buttonClasses.outline,
    buttonClasses.small
  );

  return (
    <div className={classes.form}>
      <div className={classes.block}>
        <RouteEndpoints
          startLabel={planner.startLabel}
          endLabel={planner.facility?.name ?? 'Belum ada fasilitas'}
        />

        <MutedLabel>Kategori sampah</MutedLabel>
        <PillGroup
          label="Kategori sampah"
          options={CATEGORY_OPTIONS}
          value={planner.category}
          onChange={planner.setCategory}
        />

        <MutedLabel>Fasilitas penerima terdekat</MutedLabel>
        <PillGroup
          label="Fasilitas penerima"
          options={facilityOptions}
          value={planner.facility?.id ?? null}
          onChange={planner.selectFacility}
        />

        <div className={classes.twoButtons}>
          <button
            type="button"
            className={outline}
            onClick={planner.applyMyLocation}
          >
            Pakai lokasi saya
          </button>
          <button
            type="button"
            className={outline}
            onClick={planner.togglePickOnMap}
            aria-pressed={planner.pickOnMap}
          >
            {planner.pickOnMap ? 'Batal pilih' : 'Pilih di peta'}
          </button>
        </div>
      </div>

      <div className={classes.block}>
        <ModePicker value={planner.network} onChange={planner.setNetwork} />
        <button
          type="button"
          onClick={planner.calculate}
          disabled={!planner.facility}
          className={clsx(
            buttonClasses.base,
            buttonClasses.primary,
            buttonClasses.block,
            classes.calculate
          )}
        >
          Hitung rute A*
        </button>
      </div>
    </div>
  );
}
