import { TRowAlignment } from './base-card';

export function getAlignmentStyle(rowAlignment?: TRowAlignment) {
  if (rowAlignment === 'right') {
    return 'justify-end';
  }

  if (rowAlignment === 'center') {
    return 'justify-center';
  }

  return 'justify-start';
}
