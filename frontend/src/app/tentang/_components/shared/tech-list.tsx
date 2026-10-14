import { SectionTitle } from '@/app/_components/ui/text';
import { TECH_STACK } from '@/app/_data/content';
import classes from './shared.module.css';

export function TechList() {
  return (
    <section>
      <SectionTitle>Metode &amp; teknologi</SectionTitle>
      <dl className={classes.techList}>
        {TECH_STACK.map((item) => (
          <div key={item.label} className={classes.techRow}>
            <dt className={classes.techLabel}>{item.label}</dt>
            <dd className={classes.techValue}>{item.value}</dd>
          </div>
        ))}
      </dl>
    </section>
  );
}
