import type { Metadata } from 'next';
import { ResponsiveSplit } from '@/app/_components/ui/responsive-split';
import { BerandaDesktop } from './_components/desktop/beranda-desktop';
import { BerandaMobile } from './_components/mobile/beranda-mobile';

export const metadata: Metadata = { title: 'Beranda' };

export default function BerandaPage() {
  return (
    <ResponsiveSplit desktop={<BerandaDesktop />} mobile={<BerandaMobile />} />
  );
}
