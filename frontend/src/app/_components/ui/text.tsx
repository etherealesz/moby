import type { ReactNode } from 'react';
import clsx from 'clsx';
import classes from './ui.module.css';

interface ITextProps {
  children: ReactNode;
  className?: string;
}

export function Eyebrow({ children, className }: ITextProps) {
  return <p className={clsx(classes.eyebrow, className)}>{children}</p>;
}

export function SectionTitle({
  children,
  className,
  as: Tag = 'h2',
}: ITextProps & { as?: 'h2' | 'h3' }) {
  return (
    <Tag className={clsx(classes.sectionTitle, className)}>{children}</Tag>
  );
}

export function MutedLabel({ children, className }: ITextProps) {
  return <span className={clsx(classes.label, className)}>{children}</span>;
}
