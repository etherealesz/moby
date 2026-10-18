import { MobileTopBar } from '@/app/_components/layout/mobile-top-bar';
import { PageFrame } from '@/app/_components/layout/page-frame';
import { DetectionOverlay } from '@/app/_components/ui/detection-overlay';
import { LinkButton } from '@/app/_components/ui/link-button';
import { StripedSurface } from '@/app/_components/ui/striped-surface';
import { formatDistance } from '@/app/_utils/format';
import type { ClassificationSession } from '../../_hooks/use-classification-session';
import { CameraStatus } from '../shared/camera-status';
import { CameraViewport } from '../shared/camera-viewport';
import { DetectionList } from '../shared/detection-list';
import { DisposalSteps } from '../shared/disposal-steps';
import { buildRouteHref } from '../shared/route-href';
import classes from './mobile.module.css';

export function KlasifikasiMobile({
  session,
}: {
  session: ClassificationSession;
}) {
  const { cameraActive, detections, selected, nearestRoute } = session;

  return (
    <PageFrame
      header={
        <MobileTopBar
          title="Klasifikasi"
          backHref="/"
          actions={
            <CameraStatus
              active={cameraActive}
              onToggle={session.toggleCamera}
              compact
            />
          }
        />
      }
    >
      <StripedSurface
        caption={
          cameraActive
            ? session.frameSize
              ? undefined
              : 'Menyalakan kamera…'
            : 'Kamera dihentikan'
        }
        className={classes.stage}
      >
        <CameraViewport session={session}>
          <DetectionOverlay
            detections={detections}
            selectedId={session.selectedId}
            onSelect={session.setSelectedId}
          />
        </CameraViewport>
      </StripedSurface>

      <div className={classes.content}>
        <DetectionList
          detections={detections}
          selectedId={session.selectedId}
          onSelect={session.setSelectedId}
        />
        <DisposalSteps
          selectedCategory={session.selectedCategory}
          selectedIndex={session.selectedIndex}
          isConfident={session.isConfident}
        />
        {selected && nearestRoute && (
          <div className={classes.routeAction}>
            <LinkButton
              href={buildRouteHref(selected.category, nearestRoute)}
              block
            >
              Rute ke {nearestRoute.facility.name} —{' '}
              {formatDistance(nearestRoute.distanceMeter)}
            </LinkButton>
          </div>
        )}
      </div>
    </PageFrame>
  );
}
