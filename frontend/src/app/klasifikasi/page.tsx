import type { Metadata } from 'next';
import { isDesktopRequest } from '@/app/_components/ui/device';
import { KlasifikasiView } from './_components/klasifikasi-view';

export const metadata: Metadata = { title: 'Klasifikasi' };

export default async function KlasifikasiPage() {
  return <KlasifikasiView initialDesktop={await isDesktopRequest()} />;
}
