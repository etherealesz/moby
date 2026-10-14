import { DesktopFooter } from '@/app/_components/layout/desktop-footer';
import { DesktopHeader } from '@/app/_components/layout/desktop-header';
import { PageFrame } from '@/app/_components/layout/page-frame';
import { HelpBody } from '../shared/help-body';
import { HelpSearch } from '../shared/help-search';
import { HelpToc } from './help-toc';
import classes from './desktop.module.css';

const ID_PREFIX = '';

export function BantuanDesktop() {
  return (
    <PageFrame
      header={
        <DesktopHeader
          active="/bantuan"
          subtitle="Bantuan"
          actions={
            <HelpSearch idPrefix={ID_PREFIX} className={classes.search} />
          }
        />
      }
      footer={<DesktopFooter />}
    >
      <div className={classes.body}>
        <aside className={classes.sidebar}>
          <HelpToc idPrefix={ID_PREFIX} />
        </aside>
        <div className={classes.content}>
          <HelpBody idPrefix={ID_PREFIX} layout="desktop" />
        </div>
      </div>
    </PageFrame>
  );
}
