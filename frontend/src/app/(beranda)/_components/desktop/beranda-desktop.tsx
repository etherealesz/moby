import { DesktopFooter } from '@/app/_components/layout/desktop-footer';
import { DesktopHeader } from '@/app/_components/layout/desktop-header';
import { PageFrame } from '@/app/_components/layout/page-frame';
import { LinkButton } from '@/app/_components/ui/link-button';
import { CameraPreviewPanel } from './camera-preview-panel';
import { HeroIntro } from './hero-intro';
import { ModuleGrid } from './module-grid';
import { SortingGuide } from './sorting-guide';
import classes from './desktop.module.css';

export function BerandaDesktop() {
  return (
    <PageFrame
      header={
        <DesktopHeader
          active="/"
          subtitle="MobileNet Classifier & A* Pathway"
          actions={
            <LinkButton href="/klasifikasi" size="sm">
              Mulai Klasifikasi
            </LinkButton>
          }
        />
      }
      footer={<DesktopFooter />}
    >
      <div className={classes.hero}>
        <HeroIntro />
        <CameraPreviewPanel />
      </div>
      <SortingGuide />
      <ModuleGrid />
    </PageFrame>
  );
}
