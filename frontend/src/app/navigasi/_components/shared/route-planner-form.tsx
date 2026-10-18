import clsx from 'clsx';
import { buttonClasses } from '@/app/_components/ui/link-button';
import { MutedLabel } from '@/app/_components/ui/text';
import { CATEGORY_NAMES } from '@/app/_models/moby';
import { formatDistance } from '@/app/_utils/format';
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
  const facilityOptions = planner.candidates.map((candidate) => ({
    value: candidate.facility.id,
    label: `${candidate.facility.name} · ${formatDistance(candidate.routeDistanceMeter ?? candidate.straightDistanceMeter)}`,
  }));
  const notice = planner.locationError ?? planner.error;
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
          endLabel={
            planner.facility?.name ??
            (planner.loading
              ? 'Mencari fasilitas terdekat…'
              : 'Belum ada fasilitas')
          }
        />
        {notice && (
          <p className={classes.notice} role="alert">
            {notice}
          </p>
        )}

        <MutedLabel>Kategori sampah</MutedLabel>
        <PillGroup
          label="Kategori sampah"
          options={CATEGORY_OPTIONS}
          value={planner.category}
          onChange={planner.setCategory}
        />

        <MutedLabel>Fasilitas penerima terdekat</MutedLabel>
        {facilityOptions.length > 0 ? (
          <PillGroup
            label="Fasilitas penerima"
            options={facilityOptions}
            value={planner.facilityId}
            onChange={planner.selectFacility}
          />
        ) : (
          <p className={classes.hint}>
            {planner.loading
              ? 'Menghitung rute A*…'
              : 'Daftar muncul setelah lokasi awal tersedia.'}
          </p>
        )}

        <div className={classes.twoButtons}>
          <button
            type="button"
            className={outline}
            onClick={planner.applyMyLocation}
            disabled={planner.locating}
          >
            {planner.locating ? 'Mencari lokasi…' : 'Pakai lokasi saya'}
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
          disabled={planner.loading || (!planner.route && !planner.error)}
          className={clsx(
            buttonClasses.base,
            buttonClasses.primary,
            buttonClasses.block,
            classes.calculate
          )}
        >
          {planner.loading
            ? 'Menghitung rute A*…'
            : planner.error
              ? 'Coba hitung ulang'
              : 'Lihat rute A*'}
        </button>
      </div>
    </div>
  );
}
