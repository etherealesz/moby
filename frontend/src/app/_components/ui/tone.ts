import type { Tone } from '@/app/_models/moby';
import classes from './ui.module.css';

export const TONE_CLASS: Record<Tone, string> = {
  green: classes.toneGreen,
  sage: classes.toneSage,
  gray: classes.toneGray,
  ink: classes.toneInk,
};
