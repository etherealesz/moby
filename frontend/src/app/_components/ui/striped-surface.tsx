import type { CSSProperties, ReactNode } from 'react';
import clsx from 'clsx';
import classes from './ui.module.css';

interface IStripedSurfaceProps {
  caption?: string;
  className?: string;
  style?: CSSProperties;
  children?: ReactNode;
}

export function StripedSurface({
  caption,
  className,
  style,
  children,
}: IStripedSurfaceProps) {
  return (
    <div className={clsx(classes.stripes, className)} style={style}>
      {caption && <span className={classes.stripesCaption}>{caption}</span>}
      {children}
    </div>
  );
}
