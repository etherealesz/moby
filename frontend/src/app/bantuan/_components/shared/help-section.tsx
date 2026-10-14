import type { ReactNode } from 'react';
import { SectionTitle } from '@/app/_components/ui/text';
import classes from './shared.module.css';

interface IHelpSectionProps {
  id: string;
  title: string;
  children: ReactNode;
}

export function HelpSection({ id, title, children }: IHelpSectionProps) {
  return (
    <section
      id={id}
      className={classes.section}
      aria-labelledby={`${id}-title`}
    >
      <div className={classes.sectionHead}>
        <SectionTitle>
          <span id={`${id}-title`}>{title}</span>
        </SectionTitle>
      </div>
      {children}
    </section>
  );
}
