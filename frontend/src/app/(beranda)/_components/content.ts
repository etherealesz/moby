export const HERO_TITLE = [
  'Kenali sampahnya,',
  'lalu tahu ke mana',
  'harus dibawa.',
];

export const HERO_LEAD =
  'Sistem mendeteksi objek sampah dari aliran video kamera, mengklasifikasikannya ke dalam empat kategori, lalu menghitung rute terpendek menuju fasilitas pengelolaan yang sesuai di atas graf jaringan jalan Jakarta, Tangerang, Depok, dan Bekasi.';

export const HERO_LEAD_SHORT =
  'Arahkan kamera ke sampah, sistem menentukan jenisnya dan rute ke fasilitas terdekat.';

export const MODULES = [
  {
    href: '/klasifikasi',
    title: 'Klasifikasi Sampah',
    body: 'Deteksi objek pada aliran video, klasifikasi per frame dengan penstabil label.',
  },
  {
    href: '/navigasi',
    title: 'Navigasi Rute',
    body: 'Rute terpendek A* dari posisi pengguna ke fasilitas pengolahan terdekat.',
  },
  {
    href: '/tentang',
    title: 'Tentang',
    body: 'Latar belakang, metode, teknologi, dan profil pengembang.',
  },
  {
    href: '/bantuan',
    title: 'Bantuan',
    body: 'Alur kerja antarmodul, kategori sampah, dan petunjuk peta rute.',
  },
] as const;
