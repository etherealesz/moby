export const NAV_ITEMS = [
  { href: '/', label: 'Beranda' },
  { href: '/klasifikasi', label: 'Klasifikasi' },
  { href: '/navigasi', label: 'Navigasi' },
  { href: '/tentang', label: 'Tentang' },
  { href: '/bantuan', label: 'Bantuan' },
] as const;

export type NavHref = (typeof NAV_ITEMS)[number]['href'];
