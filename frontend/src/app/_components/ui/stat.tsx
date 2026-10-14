import clsx from 'clsx';
import classes from './ui.module.css';

interface IStatProps {
  value: string | number;
  unit?: string;
  label: string;
  align?: 'center' | 'start';
  className?: string;
}

export function Stat({
  value,
  unit,
  label,
  align = 'center',
  className,
}: IStatProps) {
  return (
    <div
      className={clsx(
        classes.stat,
        align === 'start' && classes.statStart,
        className
      )}
    >
      <span className={classes.statValue}>
        {value}
        {unit && <span className={classes.statUnit}>{unit}</span>}
      </span>
      <span className={classes.label}>{label}</span>
    </div>
  );
}
