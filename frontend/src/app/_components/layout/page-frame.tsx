import type { ReactNode } from 'react';
import classes from './layout.module.css';

interface IPageFrameProps {
  header: ReactNode;
  footer?: ReactNode;
  children: ReactNode;
}

export function PageFrame({ header, footer, children }: IPageFrameProps) {
  return (
    <div className={classes.frame}>
      {header}
      <main className={classes.main}>{children}</main>
      {footer}
    </div>
  );
}
