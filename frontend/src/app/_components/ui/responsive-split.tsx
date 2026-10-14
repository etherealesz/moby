import type { ReactNode } from 'react';
import classes from './ui.module.css';

interface IResponsiveSplitProps {
  desktop: ReactNode;
  mobile: ReactNode;
}

export function ResponsiveSplit({ desktop, mobile }: IResponsiveSplitProps) {
  return (
    <>
      <div className={classes.desktopOnly}>{desktop}</div>
      <div className={classes.mobileOnly}>{mobile}</div>
    </>
  );
}
