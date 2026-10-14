'use client';

import { useMediaQuery } from '@mantine/hooks';

const DESKTOP_MEDIA_QUERY = '(min-width: 62em)';

export function useIsDesktop(initialDesktop: boolean) {
  return useMediaQuery(DESKTOP_MEDIA_QUERY, initialDesktop, {
    getInitialValueInEffect: true,
  });
}
