import type { CategoryName, IDetection } from '@/app/_models/moby';

const API_BASE_URL =
  process.env.NEXT_PUBLIC_TRASH_NAV_API_BASE_URL || 'http://localhost:8000';

export const CLASSIFY_WS_URL = `${API_BASE_URL.replace(/^http/, 'ws')}/moby/ws/classify`;

interface IClassifiedObject {
  track_id: number | null;
  box: { x1: number; y1: number; x2: number; y2: number };
  label: CategoryName;
  confidence: number;
  detection_confidence: number;
  probabilities: Record<CategoryName, number>;
}

export interface IClassifyFrame {
  width: number;
  height: number;
  objects: IClassifiedObject[];
  total_time_ms: number;
}

export interface IClassifyMessage {
  data: IClassifyFrame | null;
  error: { message: string } | null;
}

export interface ITrackHistory {
  category: CategoryName;
  stableFrames: number;
}

const ERROR_MESSAGES: Record<string, string> = {
  DETECTOR_MODEL_NOT_AVAILABLE: 'Bobot model deteksi belum tersedia di server.',
  CLASSIFIER_MODEL_NOT_AVAILABLE:
    'Bobot model klasifikasi belum tersedia di server.',
  CLASSIFIER_LABEL_MISMATCH: 'Label bobot klasifikasi tidak sesuai.',
  INVALID_IMAGE: 'Frame tidak dapat dibaca server.',
};

export function describeServerError(message: string) {
  return ERROR_MESSAGES[message] ?? `Server: ${message}`;
}

export function toDetections(
  frame: IClassifyFrame,
  history: Map<number, ITrackHistory>
): IDetection[] {
  const seen = new Set<number>();

  const detections = frame.objects.map((object, index) => {
    const trackId = object.track_id ?? -(index + 1);
    const previous = history.get(trackId);
    const stableFrames =
      previous?.category === object.label ? previous.stableFrames + 1 : 1;
    history.set(trackId, { category: object.label, stableFrames });
    seen.add(trackId);

    const { x1, y1, x2, y2 } = object.box;
    return {
      id: `obj-${trackId}`,
      category: object.label,
      confidence: object.confidence,
      stableFrames,
      box: {
        x: x1 / frame.width,
        y: y1 / frame.height,
        w: (x2 - x1) / frame.width,
        h: (y2 - y1) / frame.height,
      },
    };
  });

  for (const trackId of history.keys()) {
    if (!seen.has(trackId)) {
      history.delete(trackId);
    }
  }
  return detections;
}
