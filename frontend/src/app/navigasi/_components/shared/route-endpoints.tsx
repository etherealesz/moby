import clsx from 'clsx';
import classes from './shared.module.css';

interface IRouteEndpointsProps {
  startLabel: string;
  endLabel: string;
}

export function RouteEndpoints({ startLabel, endLabel }: IRouteEndpointsProps) {
  return (
    <div className={classes.endpoints}>
      <div className={classes.rail} aria-hidden>
        <span className={clsx(classes.railDot, classes.railStart)} />
        <span className={classes.railLine} />
        <span className={clsx(classes.railDot, classes.railEnd)} />
      </div>
      <div className={classes.fields}>
        <div className={classes.field}>
          <span className={classes.fieldLabel}>Titik awal (A)</span>
          <output className={classes.fieldValue}>{startLabel}</output>
        </div>
        <div className={classes.field}>
          <span className={classes.fieldLabel}>Titik tujuan (B)</span>
          <output className={classes.fieldValue}>{endLabel}</output>
        </div>
      </div>
    </div>
  );
}
