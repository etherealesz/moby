import type { Metadata } from 'next';
import { ResponsiveSplit } from '@/app/_components/ui/responsive-split';
import { BantuanDesktop } from './_components/desktop/bantuan-desktop';
import { BantuanMobile } from './_components/mobile/bantuan-mobile';

export const metadata: Metadata = { title: 'Bantuan' };

export default function BantuanPage() {
  return (
    <ResponsiveSplit desktop={<BantuanDesktop />} mobile={<BantuanMobile />} />
  );
}
