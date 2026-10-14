import clsx from 'clsx';
import { DesktopFooter } from '@/app/_components/layout/desktop-footer';
import { DesktopHeader } from '@/app/_components/layout/desktop-header';
import { PageFrame } from '@/app/_components/layout/page-frame';
import { buttonClasses } from '@/app/_components/ui/link-button';
import type { ClassificationSession } from '../../_hooks/use-classification-session';
import { CameraStatus } from '../shared/camera-status';
import { DetectionList } from '../shared/detection-list';
import { DisposalSteps } from '../shared/disposal-steps';
import { CameraStage } from './camera-stage';
import { NearestFacility } from './nearest-facility';
import classes from './desktop.module.css';

export function KlasifikasiDesktop({
  session,
}: {
  session: ClassificationSession;
}) {
  return (
    <PageFrame
      header={
        <DesktopHeader
          active="/klasifikasi"
          subtitle="Klasifikasi sampah"
          actions={
            <>
              <CameraStatus
                active={session.cameraActive}
                onToggle={session.toggleCamera}
              />
              <button
                type="button"
                onClick={session.toggleCamera}
                className={clsx(
                  buttonClasses.base,
                  buttonClasses.outline,
                  buttonClasses.small
                )}
              >
                {session.cameraActive ? 'Hentikan' : 'Mulai'}
              </button>
            </>
          }
        />
      }
      footer={<DesktopFooter />}
    >
      <div className={classes.body}>
        <CameraStage session={session} />
        <aside className={classes.sidebar}>
          <DetectionList
            detections={session.detections}
            selectedId={session.selectedId}
            onSelect={session.setSelectedId}
          />
          <DisposalSteps
            selectedCategory={session.selectedCategory}
            selectedIndex={session.selectedIndex}
            isConfident={session.isConfident}
          />
          <NearestFacility
            nearestRoute={session.nearestRoute}
            selected={session.selected}
          />
        </aside>
      </div>
    </PageFrame>
  );
}
