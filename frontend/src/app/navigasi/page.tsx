import type { Metadata } from 'next';
import { isDesktopRequest } from '@/app/_components/ui/device';
import { CATEGORY_NAMES, type CategoryName } from '@/app/_models/moby';
import { NavigasiView } from './_components/navigasi-view';

export const metadata: Metadata = { title: 'Navigasi' };

interface INavigasiPageProps {
  searchParams: Promise<{ kategori?: string; fasilitas?: string }>;
}

function parseCategory(value?: string): CategoryName {
  return CATEGORY_NAMES.find((name) => name === value) ?? 'Anorganik';
}

function parseFacilityId(value?: string): number | null {
  const id = Number(value);
  return Number.isInteger(id) && id > 0 ? id : null;
}

export default async function NavigasiPage({
  searchParams,
}: INavigasiPageProps) {
  const params = await searchParams;

  return (
    <NavigasiView
      initialDesktop={await isDesktopRequest()}
      initialCategory={parseCategory(params.kategori)}
      initialFacilityId={parseFacilityId(params.fasilitas)}
    />
  );
}
