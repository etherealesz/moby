import type { CategoryName, IWasteCategory } from '@/app/_models/moby';

export const CONFIDENCE_THRESHOLD = 0.5;

export const WASTE_CATEGORIES: IWasteCategory[] = [
  {
    id: 1,
    name: 'Anorganik',
    code: 'ANO',
    tone: 'green',
    subcategories: ['Plastik', 'Kertas dan Karton', 'Kaca', 'Logam', 'Tekstil'],
    disposalSteps: [
      'Kosongkan dan bilas wadah.',
      'Lepaskan tutup dan label bila memungkinkan.',
      'Pipihkan atau lipat agar ringkas.',
      'Bawa ke bank sampah terdekat.',
    ],
    facilityTypes: ['Bank Sampah'],
  },
  {
    id: 2,
    name: 'B3',
    code: 'B3',
    tone: 'ink',
    subcategories: [
      'Baterai',
      'Elektronik Kecil',
      'Lampu',
      'Kemasan Bertekanan',
    ],
    disposalSteps: [
      'Jangan dicampur dengan sampah lain.',
      'Simpan dalam wadah tertutup dan kering.',
      'Jangan dibakar, ditusuk, atau dibongkar.',
      'Bawa ke TPST atau TPA.',
    ],
    facilityTypes: ['TPST', 'TPA'],
  },
  {
    id: 3,
    name: 'Organik',
    code: 'ORG',
    tone: 'sage',
    subcategories: [
      'Sisa Makanan',
      'Kulit Buah',
      'Sisa Bahan Dapur',
      'Daun dan Ranting',
    ],
    disposalSteps: [
      'Pisahkan dari plastik dan kemasan.',
      'Tiriskan sisa cairan.',
      'Bawa ke TPS3R untuk dikomposkan.',
    ],
    facilityTypes: ['TPS3R'],
  },
  {
    id: 4,
    name: 'Residu',
    code: 'RES',
    tone: 'gray',
    subcategories: [
      'Produk Sanitasi Sekali Pakai',
      'Kemasan Saset',
      'Styrofoam',
      'Puntung Rokok',
    ],
    disposalSteps: [
      'Masukkan ke kantong tertutup.',
      'Jangan dicampur dengan sampah daur ulang.',
      'Bawa ke TPST atau TPA.',
    ],
    facilityTypes: ['TPST', 'TPA'],
  },
];

export const SUBCATEGORY_COUNT = WASTE_CATEGORIES.reduce(
  (total, category) => total + category.subcategories.length,
  0
);

export function getCategory(name: CategoryName): IWasteCategory {
  const category = WASTE_CATEGORIES.find((item) => item.name === name);
  if (!category) {
    throw new Error(`Kategori tidak dikenal: ${name}`);
  }
  return category;
}
