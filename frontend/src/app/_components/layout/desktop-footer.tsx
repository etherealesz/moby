import { FOOTER_TAGLINE } from '@/app/_data/content';
import classes from './layout.module.css';

export function DesktopFooter() {
  return (
    <footer className={classes.footer}>
      <span className={classes.footerLogo}>MOBY</span>
      <span className={classes.footerTag}>{FOOTER_TAGLINE}</span>
    </footer>
  );
}
