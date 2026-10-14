import type { Metadata } from 'next';
import { ResponsiveSplit } from '@/app/_components/ui/responsive-split';
import { TentangDesktop } from './_components/desktop/tentang-desktop';
import { TentangMobile } from './_components/mobile/tentang-mobile';

export const metadata: Metadata = { title: 'Tentang' };

export default function TentangPage() {
  return (
    <ResponsiveSplit desktop={<TentangDesktop />} mobile={<TentangMobile />} />
  );
}
