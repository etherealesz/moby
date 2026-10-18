export const CATEGORY_NAMES = ['Anorganik', 'B3', 'Organik', 'Residu'] as const;
export type CategoryName = (typeof CATEGORY_NAMES)[number];

export type FacilityType = 'Bank Sampah' | 'TPS3R' | 'TPST' | 'TPA';
export type NetworkType = 'walk' | 'drive';
export type Tone = 'green' | 'sage' | 'gray' | 'ink';
export type LatLon = [number, number];

export interface IWasteCategory {
  id: number;
  name: CategoryName;
  code: string;
  tone: Tone;
  subcategories: string[];
  disposalSteps: string[];
  facilityTypes: FacilityType[];
}

export interface INormalizedBox {
  x: number;
  y: number;
  w: number;
  h: number;
}

export interface IDetection {
  id: string;
  category: CategoryName;
  confidence: number;
  stableFrames: number;
  box: INormalizedBox;
}

export interface IFacility {
  id: number;
  name: string;
  type: FacilityType;
  address: string;
  city: string;
  openHours?: string;
  position: LatLon;
}

export interface IRouteResult {
  facility: IFacility;
  path: LatLon[];
  distanceMeter: number;
  etaMinutes: number;
  network: NetworkType;
}
