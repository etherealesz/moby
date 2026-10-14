import Link from 'next/link';
import clsx from 'clsx';
import { formatIndex } from '@/app/_components/ui/detection-overlay';
import { SectionTitle } from '@/app/_components/ui/text';
import { MODULES } from '../content';
import classes from './desktop.module.css';

export function ModuleGrid() {
  return (
    <section className={classes.section}>
      <div className={classes.sectionHead}>
        <SectionTitle>Modul sistem</SectionTitle>
      </div>

      <div className={classes.grid3}>
        {MODULES.map((module, index) => (
          <Link
            key={module.href}
            href={module.href}
            className={clsx(classes.cell, classes.moduleCard)}
          >
            <span className={classes.moduleIndex}>{formatIndex(index)}</span>
            <h3 className={classes.moduleTitle}>{module.title}</h3>
            <p className={classes.moduleBody}>{module.body}</p>
          </Link>
        ))}
        <div className={clsx(classes.cell, classes.closing)}>
          <p className={classes.closingTitle}>
            Buang di tempat
            <br />
            yang benar.
          </p>
          <span className={classes.closingMeta}>MOBY · 2026</span>
        </div>
      </div>
    </section>
  );
}
