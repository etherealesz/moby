import clsx from 'clsx';
import { DetectionOverlay } from '@/app/_components/ui/detection-overlay';
import { buttonClasses } from '@/app/_components/ui/link-button';
import { StripedSurface } from '@/app/_components/ui/striped-surface';
import { MutedLabel } from '@/app/_components/ui/text';
import type { ClassificationSession } from '../../_hooks/use-classification-session';
import { CameraViewport } from '../shared/camera-viewport';
import classes from './desktop.module.css';

const toolButton = clsx(
  buttonClasses.base,
  buttonClasses.outline,
  buttonClasses.small
);

export function CameraStage({ session }: { session: ClassificationSession }) {
  const { cameraActive, showBoxes, detections, selectedId, frameSize } =
    session;

  return (
    <div className={classes.stageColumn}>
      <StripedSurface
        caption={
          cameraActive
            ? frameSize
              ? undefined
              : 'Menyalakan kamera…'
            : 'Kamera dihentikan'
        }
        className={classes.stage}
      >
        <CameraViewport session={session}>
          {showBoxes && (
            <DetectionOverlay
              detections={detections}
              selectedId={selectedId}
              onSelect={session.setSelectedId}
            />
          )}
        </CameraViewport>
      </StripedSurface>

      <div className={classes.toolbar}>
        <button
          type="button"
          className={toolButton}
          onClick={() => void session.switchCamera()}
          disabled={!cameraActive}
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
        {frameSize && (
          <MutedLabel>
            {frameSize.width} × {frameSize.height}
            {session.latencyMs !== null &&
              ` · ${Math.round(session.latencyMs)} ms/frame`}
          </MutedLabel>
        )}
      </div>
    </div>
  );
}
