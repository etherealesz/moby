import type { ReactNode } from 'react';
import Link from 'next/link';
import { LuChevronLeft } from 'react-icons/lu';
import classes from './layout.module.css';

interface IMobileTopBarProps {
  title: string;
  backHref?: string;
  onBack?: () => void;
  actions?: ReactNode;
}

export function MobileTopBar({
  title,
  backHref,
  onBack,
  actions,
}: IMobileTopBarProps) {
  const backIcon = <LuChevronLeft size={24} aria-hidden />;

  return (
    <header className={classes.topBar}>
      <div className={classes.topBarStart}>
        {backHref && (
          <Link
            href={backHref}
            className={classes.backButton}
            aria-label="Kembali"
          >
            {backIcon}
          </Link>
        )}
        {!backHref && onBack && (
          <button
            type="button"
            onClick={onBack}
            className={classes.backButton}
            aria-label="Kembali"
          >
            {backIcon}
          </button>
        )}
        <span className={classes.topBarTitle}>{title}</span>
      </div>
      {actions}
    </header>
  );
}
