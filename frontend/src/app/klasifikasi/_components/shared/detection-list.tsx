import clsx from 'clsx';
import { ConfidenceBar } from '@/app/_components/ui/confidence-bar';
import { formatIndex } from '@/app/_components/ui/detection-overlay';
import { MutedLabel, SectionTitle } from '@/app/_components/ui/text';
import { CONFIDENCE_THRESHOLD, getCategory } from '@/app/_data/categories';
import type { IDetection, Tone } from '@/app/_models/moby';
import classes from './shared.module.css';

interface IDetectionListProps {
  detections: IDetection[];
  selectedId: string | null;
  onSelect: (id: string) => void;
}

export function DetectionList({
  detections,
  selectedId,
  onSelect,
}: IDetectionListProps) {
  return (
    <section aria-label="Objek terdeteksi">
      <div className={classes.listHead}>
        <SectionTitle>Objek terdeteksi</SectionTitle>
        <MutedLabel>{detections.length} objek</MutedLabel>
      </div>

      {detections.length === 0 ? (
        <p className={classes.empty}>Belum ada objek. Nyalakan kamera.</p>
      ) : (
        <ul className={classes.list}>
          {detections.map((detection, index) => {
            const isSelected = detection.id === selectedId;
            const isLow = detection.confidence < CONFIDENCE_THRESHOLD;
            const tone: Tone = isLow ? 'gray' : isSelected ? 'green' : 'ink';
            const meta = isLow
              ? `Di bawah ambang ${CONFIDENCE_THRESHOLD.toFixed(2)}`
              : `Stabil ${detection.stableFrames} frame · ${getCategory(detection.category).facilityTypes.join(' / ')}`;

            return (
              <li key={detection.id}>
                <button
                  type="button"
                  onClick={() => onSelect(detection.id)}
                  aria-pressed={isSelected}
                  className={clsx(
                    classes.item,
                    isSelected && classes.itemSelected,
                    isLow && classes.itemLow
                  )}
                >
                  <span className={classes.itemIndex}>
                    {formatIndex(index)}
                  </span>
                  <span className={classes.itemName}>{detection.category}</span>
                  <span className={classes.itemScore}>
                    {detection.confidence.toFixed(2)}
                  </span>
                  <MutedLabel className={classes.itemMeta}>{meta}</MutedLabel>
                  <ConfidenceBar
                    value={detection.confidence}
                    tone={tone}
                    showValue={false}
                    className={classes.itemBar}
                  />
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}
