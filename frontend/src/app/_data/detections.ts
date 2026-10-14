import type { IDetection } from '@/app/_models/moby';

export const DUMMY_DETECTIONS: IDetection[] = [
  {
    id: 'obj-1',
    category: 'Anorganik',
    confidence: 0.97,
    stableFrames: 12,
    box: { x: 0.06, y: 0.2, w: 0.33, h: 0.56 },
  },
  {
    id: 'obj-2',
    category: 'Residu',
    confidence: 0.84,
    stableFrames: 9,
    box: { x: 0.47, y: 0.38, w: 0.22, h: 0.38 },
  },
  {
    id: 'obj-3',
    category: 'Organik',
    confidence: 0.42,
    stableFrames: 2,
    box: { x: 0.76, y: 0.52, w: 0.17, h: 0.26 },
  },
];

export const DUMMY_STREAM_LABEL = 'Aliran video kamera · 1280 × 720';
