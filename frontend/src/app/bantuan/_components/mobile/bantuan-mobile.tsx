import { MobileTopBar } from '@/app/_components/layout/mobile-top-bar';
import { PageFrame } from '@/app/_components/layout/page-frame';
import { HelpBody } from '../shared/help-body';
import { HelpSearch } from '../shared/help-search';
import classes from './mobile.module.css';

// Versi desktop dirender bersamaan, jadi id seksi diberi prefix berbeda.
const ID_PREFIX = 'm-';

export function BantuanMobile() {
  return (
    <PageFrame header={<MobileTopBar title="Bantuan" backHref="/" />}>
      <div className={classes.searchBar}>
        <HelpSearch idPrefix={ID_PREFIX} />
      </div>
      <div className={classes.content}>
        <HelpBody idPrefix={ID_PREFIX} layout="mobile" />
      </div>
    </PageFrame>
  );
}
