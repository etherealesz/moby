import clsx from 'clsx';
import { CONFIDENCE_THRESHOLD } from '@/app/_data/categories';
import type { IDetection } from '@/app/_models/moby';
import classes from './ui.module.css';

interface IDetectionOverlayProps {
  detections: IDetection[];
  selectedId?: string | null;
  onSelect?: (id: string) => void;
  numbered?: boolean;
  showCount?: boolean;
}

export function formatIndex(index: number) {
  return String(index + 1).padStart(2, '0');
}

export function DetectionOverlay({
  detections,
  selectedId,
  onSelect,
  numbered = true,
  showCount = true,
}: IDetectionOverlayProps) {
  return (
    <div className={classes.overlay}>
      {showCount && (
        <span className={classes.countBadge}>{detections.length} objek</span>
      )}
      {detections.map((detection, index) => {
        const { x, y, w, h } = detection.box;
        const isLow = detection.confidence < CONFIDENCE_THRESHOLD;
        const label = (
          <span className={classes.boxLabel}>
            {numbered && <span>{formatIndex(index)}</span>}
            <span>{detection.category}</span>
            <span>{detection.confidence.toFixed(2)}</span>
          </span>
        );
        const boxClass = clsx(
          classes.box,
          detection.id === selectedId && classes.boxSelected,
          isLow && classes.boxLow
        );
        const style = {
          left: `${x * 100}%`,
          top: `${y * 100}%`,
          width: `${w * 100}%`,
          height: `${h * 100}%`,
        };

        return onSelect ? (
          <button
            key={detection.id}
            type="button"
            className={boxClass}
            style={style}
            onClick={() => onSelect(detection.id)}
            aria-label={`Pilih objek ${formatIndex(index)} ${detection.category}`}
          >
            {label}
          </button>
        ) : (
          <div key={detection.id} className={boxClass} style={style}>
            {label}
          </div>
        );
      })}
    </div>
  );
}
