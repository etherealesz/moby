import type { ReactNode } from 'react';
import Link from 'next/link';
import clsx from 'clsx';
import classes from './ui.module.css';

interface ILinkButtonProps {
  href: string;
  children: ReactNode;
  variant?: 'primary' | 'outline';
  size?: 'md' | 'sm';
  block?: boolean;
  className?: string;
}

export function LinkButton({
  href,
  children,
  variant = 'primary',
  size = 'md',
  block = false,
  className,
}: ILinkButtonProps) {
  return (
    <Link
      href={href}
      className={clsx(
        classes.btn,
        variant === 'primary' ? classes.btnPrimary : classes.btnOutline,
        size === 'sm' && classes.btnSmall,
        block && classes.btnBlock,
        className
      )}
    >
      {children}
    </Link>
  );
}

export const buttonClasses = {
  base: classes.btn,
  primary: classes.btnPrimary,
  outline: classes.btnOutline,
  small: classes.btnSmall,
  block: classes.btnBlock,
};
