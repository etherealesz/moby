import { ConfidenceBar } from '@/app/_components/ui/confidence-bar';
import { DetectionOverlay } from '@/app/_components/ui/detection-overlay';
import { LinkButton } from '@/app/_components/ui/link-button';
import { StripedSurface } from '@/app/_components/ui/striped-surface';
import { MutedLabel } from '@/app/_components/ui/text';
import { getCategory } from '@/app/_data/categories';
import { DUMMY_DETECTIONS } from '@/app/_data/detections';
import classes from './desktop.module.css';

const PREVIEW_DETECTIONS = DUMMY_DETECTIONS.slice(0, 2);
const TOP = PREVIEW_DETECTIONS[0];

export function CameraPreviewPanel() {
  return (
    <section className={classes.preview} aria-label="Pratinjau kamera">
      <div className={classes.previewHead}>
        <span className={classes.previewTitle}>Pratinjau kamera</span>
        <span className={classes.liveTag}>Aktif</span>
      </div>

      <StripedSurface
        caption="Aliran video 640 × 480"
        className={classes.previewStage}
      >
        <DetectionOverlay
          detections={PREVIEW_DETECTIONS}
          selectedId={TOP.id}
          numbered={false}
          showCount={false}
        />
      </StripedSurface>

      <div className={classes.previewBody}>
        <MutedLabel>Prediksi teratas</MutedLabel>
        <h2 className={classes.predictionName}>{TOP.category}</h2>
        <p className={classes.predictionMeta}>
          Dibawa ke {getCategory(TOP.category).facilityTypes.join(' / ')} ·
          label stabil {TOP.stableFrames} frame berturut-turut
        </p>
        <ConfidenceBar value={TOP.confidence} />
        <LinkButton href="/navigasi" variant="outline" size="sm" block>
          Cari fasilitas terdekat →
        </LinkButton>
      </div>
    </section>
  );
}
