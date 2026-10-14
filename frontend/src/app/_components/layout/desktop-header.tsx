import type { ReactNode } from 'react';
import Link from 'next/link';
import clsx from 'clsx';
import { NAV_ITEMS, type NavHref } from './nav-items';
import classes from './layout.module.css';

interface IDesktopHeaderProps {
  active: NavHref;
  subtitle: string;
  actions?: ReactNode;
}

export function DesktopHeader({
  active,
  subtitle,
  actions,
}: IDesktopHeaderProps) {
  return (
    <header className={classes.header}>
      <Link href="/" className={classes.brand}>
        <span className={classes.logo}>MOBY</span>
        <span className={classes.subtitle}>{subtitle}</span>
      </Link>

      <nav className={classes.nav} aria-label="Navigasi utama">
        {NAV_ITEMS.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            aria-current={item.href === active ? 'page' : undefined}
            className={clsx(
              classes.navLink,
              item.href === active && classes.navLinkActive
            )}
          >
            {item.label}
          </Link>
        ))}
      </nav>

      <div className={classes.headerActions}>{actions}</div>
    </header>
  );
}
