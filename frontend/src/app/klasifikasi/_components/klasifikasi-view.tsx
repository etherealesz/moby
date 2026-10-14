'use client';

import { useIsDesktop } from '@/app/_components/ui/use-is-desktop';
import { useClassificationSession } from '../_hooks/use-classification-session';
import { KlasifikasiDesktop } from './desktop/klasifikasi-desktop';
import { KlasifikasiMobile } from './mobile/klasifikasi-mobile';

export function KlasifikasiView({
  initialDesktop,
}: {
  initialDesktop: boolean;
}) {
  const isDesktop = useIsDesktop(initialDesktop);
  const session = useClassificationSession();

  return isDesktop ? (
    <KlasifikasiDesktop session={session} />
  ) : (
    <KlasifikasiMobile session={session} />
  );
}
