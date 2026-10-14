import { MutedLabel } from '@/app/_components/ui/text';
import { HELP_SECTIONS } from '@/app/_data/content';
import classes from './desktop.module.css';

export function HelpToc({ idPrefix }: { idPrefix: string }) {
  return (
    <nav className={classes.toc} aria-label="Isi panduan">
      <MutedLabel className={classes.tocTitle}>Isi panduan</MutedLabel>
      <ul className={classes.tocList}>
        {HELP_SECTIONS.map((section) => (
          <li key={section.id}>
            <a href={`#${idPrefix}${section.id}`} className={classes.tocLink}>
              {section.label}
            </a>
          </li>
        ))}
      </ul>
    </nav>
  );
}
