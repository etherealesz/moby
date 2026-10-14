import clsx from 'clsx';
import type { Tone } from '@/app/_models/moby';
import { TONE_CLASS } from './tone';
import classes from './ui.module.css';

export function CategorySwatch({ tone }: { tone: Tone }) {
  return (
    <span className={clsx(classes.swatch, TONE_CLASS[tone])} aria-hidden />
  );
}
