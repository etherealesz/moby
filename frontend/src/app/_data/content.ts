export const TECH_STACK = [
  { label: 'Praproses citra', value: 'CIELAB · CLAHE' },
  { label: 'Deteksi objek', value: 'YOLO26' },
  { label: 'Klasifikasi', value: 'MobileNetV4-Conv-S' },
  { label: 'Penstabil label', value: 'Temporal smoothing' },
  { label: 'Graf jalan', value: 'OSMnx · OpenStreetMap' },
  { label: 'Pencarian rute', value: 'A* Search' },
  { label: 'Antarmuka', value: 'Next.js · Mantine' },
] as const;

export const SYSTEM_FLOW = [
  { title: 'Aliran video', body: 'Frame dibaca dari kamera perangkat.' },
  { title: 'Deteksi objek', body: 'YOLO26 menghasilkan kotak pembatas.' },
  {
    title: 'Klasifikasi',
    body: 'MobileNetV4 menentukan kategori sampah.',
  },
  {
    title: 'Fasilitas cocok',
    body: 'Sistem memilih fasilitas penerima kategori itu.',
  },
  {
    title: 'Rute A*',
    body: 'Jalur terpendek dihitung di atas graf jalan.',
  },
] as const;

export const DEVELOPER = {
  name: 'Enardo Stefanus',
  affiliation: 'Teknik Informatika, Universitas Tarumanagara, 2026',
  email: 'enardo.535230072@stu.untar.ac.id',
} as const;

export const FOOTER_TAGLINE = 'YOLO26 · MobileNetV4 · OSMnx · A* Search';

export const HELP_SECTIONS = [
  { id: 'memulai', label: 'Memulai', keywords: 'langkah mulai awal' },
  {
    id: 'kamera',
    label: 'Menggunakan kamera',
    keywords: 'izin cahaya jarak video',
  },
  {
    id: 'hasil',
    label: 'Membaca hasil klasifikasi',
    keywords: 'skor keyakinan label stabil frame kotak',
  },
  {
    id: 'kategori',
    label: 'Kategori sampah',
    keywords: 'anorganik b3 organik residu bank sampah tps3r tpst tpa',
  },
  {
    id: 'peta',
    label: 'Peta dan rute',
    keywords: 'titik awal tujuan garis rute a* gps',
  },
  {
    id: 'masalah',
    label: 'Masalah umum',
    keywords: 'error tidak muncul meleset gagal ditemukan berganti',
  },
] as const;

export const HELP_STEPS = [
  {
    title: 'Izinkan kamera',
    body: 'Buka Klasifikasi lalu izinkan akses kamera pada peramban. Arahkan objek ke tengah bingkai.',
  },
  {
    title: 'Tunggu label stabil',
    body: 'Label dianggap valid setelah bertahan beberapa frame. Kotak putus-putus berarti keyakinan di bawah ambang.',
  },
  {
    title: 'Hitung rute',
    body: 'Tekan “Hitung rute ke fasilitas”, periksa titik A dan B, pilih mode perjalanan, lalu hitung rute A*.',
  },
] as const;

export const HELP_CAMERA_TIPS = [
  'Gunakan cahaya yang cukup; sistem memperbaiki kontras secara otomatis, tetapi tidak bisa melihat dalam gelap.',
  'Jaga jarak 30–60 cm agar objek terlihat utuh.',
  'Satu frame boleh berisi beberapa objek; setiap objek diberi nomor sendiri.',
] as const;

export const HELP_READING = [
  {
    term: 'Nomor objek',
    body: 'Urutan objek di daftar, sama dengan nomor di atas kotak.',
  },
  {
    term: 'Skor keyakinan',
    body: 'Angka 0–1 dari Softmax; makin dekat 1 makin yakin.',
  },
  {
    term: 'Stabil N frame',
    body: 'Label tidak berubah selama N frame berturut-turut.',
  },
] as const;

export const HELP_MAP_LEGEND = [
  {
    mark: 'A',
    tone: 'green',
    title: 'Titik awal',
    body: 'Posisi Anda, dari GPS atau klik pada peta.',
  },
  {
    mark: 'B',
    tone: 'ink',
    title: 'Fasilitas tujuan',
    body: 'Fasilitas yang menerima kategori sampah tersebut.',
  },
  {
    mark: 'line',
    tone: 'green',
    title: 'Garis tebal hijau',
    body: 'Rute terpendek hasil A* Search.',
  },
] as const;

export const HELP_FAQ = [
  {
    question: 'Kamera tidak muncul di peramban',
    answer:
      'Pastikan izin kamera diberikan dan halaman dibuka lewat HTTPS atau localhost. Tutup aplikasi lain yang sedang memakai kamera.',
  },
  {
    question: 'Label berganti-ganti terus',
    answer:
      'Tahan kamera lebih diam dan dekatkan objek. Penstabil label baru mengganti label bila kelas baru unggul beberapa frame berturut-turut.',
  },
  {
    question: 'Rute tidak ditemukan',
    answer:
      'Titik awal mungkin di luar wilayah graf (Jakarta, Tangerang, Depok, Bekasi) atau jauh dari jalan. Coba pilih titik lain di peta.',
  },
  {
    question: 'GPS meleset jauh',
    answer:
      'Aktifkan mode akurasi tinggi di perangkat, atau tentukan titik awal secara manual dengan “Pilih di peta”.',
  },
] as const;
