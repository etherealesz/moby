import clsx from 'clsx';
import { notifications } from '@mantine/notifications';
import { DetectionOverlay } from '@/app/_components/ui/detection-overlay';
import { buttonClasses } from '@/app/_components/ui/link-button';
import { StripedSurface } from '@/app/_components/ui/striped-surface';
import { DUMMY_STREAM_LABEL } from '@/app/_data/detections';
import type { ClassificationSession } from '../../_hooks/use-classification-session';
import classes from './desktop.module.css';

const toolButton = clsx(
  buttonClasses.base,
  buttonClasses.outline,
  buttonClasses.small
);

export function CameraStage({ session }: { session: ClassificationSession }) {
  const { cameraActive, showBoxes, detections, selectedId } = session;

  return (
    <div className={classes.stageColumn}>
      <StripedSurface
        caption={cameraActive ? DUMMY_STREAM_LABEL : 'Kamera dihentikan'}
        className={classes.stage}
      >
        {cameraActive && showBoxes && (
          <DetectionOverlay
            detections={detections}
            selectedId={selectedId}
            onSelect={session.setSelectedId}
          />
        )}
      </StripedSurface>

      <div className={classes.toolbar}>
        <button
          type="button"
          className={toolButton}
          onClick={() =>
            notifications.show({
              message: 'Pilihan kamera belum tersedia (data dummy).',
            })
          }
        >
          Ganti kamera
        </button>
        <button
          type="button"
          className={toolButton}
          onClick={session.toggleBoxes}
          aria-pressed={showBoxes}
        >
          Kotak pembatas: {showBoxes ? 'aktif' : 'nonaktif'}
        </button>
      </div>
    </div>
  );
}
