import clsx from 'clsx';
import type { Tone } from '@/app/_models/moby';
import { TONE_CLASS } from './tone';
import classes from './ui.module.css';

interface IConfidenceBarProps {
  value: number;
  tone?: Tone;
  showValue?: boolean;
  className?: string;
}

export function ConfidenceBar({
  value,
  tone = 'green',
  showValue = true,
  className,
}: IConfidenceBarProps) {
  const percent = Math.round(Math.min(Math.max(value, 0), 1) * 100);

  return (
    <div className={clsx(classes.bar, className)}>
      <div
        className={clsx(classes.barTrack, TONE_CLASS[tone])}
        role="meter"
        aria-label="Skor keyakinan"
        aria-valuemin={0}
        aria-valuemax={1}
        aria-valuenow={value}
      >
        <div className={classes.barFill} style={{ width: `${percent}%` }} />
      </div>
      {showValue && (
        <span className={classes.barValue}>{value.toFixed(2)}</span>
      )}
    </div>
  );
}
