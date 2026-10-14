import type { IFacility, LatLon } from '@/app/_models/moby';

export const DUMMY_FACILITIES: IFacility[] = [
  {
    id: 1,
    name: 'Bank Sampah Beji',
    type: 'Bank Sampah',
    address: 'Jl. Beji Timur No. 14',
    city: 'Depok',
    openHours: '06.00–16.00',
    position: [-6.3688, 106.8262],
  },
  {
    id: 2,
    name: 'Bank Sampah Kukusan',
    type: 'Bank Sampah',
    address: 'Jl. Kukusan Raya No. 3',
    city: 'Depok',
    openHours: '07.00–15.00',
    position: [-6.3655, 106.8178],
  },
  {
    id: 3,
    name: 'Bank Sampah Pondok Cina',
    type: 'Bank Sampah',
    address: 'Jl. Margonda Raya No. 210',
    city: 'Depok',
    openHours: '08.00–16.00',
    position: [-6.3712, 106.8321],
  },
  {
    id: 4,
    name: 'TPS3R Beji',
    type: 'TPS3R',
    address: 'Jl. Beji Permai No. 5',
    city: 'Depok',
    openHours: '06.00–16.00',
    position: [-6.3801, 106.8219],
  },
  {
    id: 5,
    name: 'TPS3R Tanah Baru',
    type: 'TPS3R',
    address: 'Jl. Tanah Baru No. 21',
    city: 'Depok',
    openHours: '06.00–14.00',
    position: [-6.3843, 106.8105],
  },
  {
    id: 6,
    name: 'TPST Pancoran Mas',
    type: 'TPST',
    address: 'Jl. Raya Sawangan No. 8',
    city: 'Depok',
    openHours: '05.00–17.00',
    position: [-6.3935, 106.8012],
  },
  {
    id: 7,
    name: 'TPA Cipayung',
    type: 'TPA',
    address: 'Jl. Cipayung Jaya',
    city: 'Depok',
    openHours: '24 jam',
    position: [-6.4268, 106.7905],
  },
];

export const DUMMY_USER_POSITION: LatLon = [-6.3762, 106.8148];
