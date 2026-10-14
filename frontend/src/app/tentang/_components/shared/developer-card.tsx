import { StripedSurface } from '@/app/_components/ui/striped-surface';
import { SectionTitle } from '@/app/_components/ui/text';
import { DEVELOPER } from '@/app/_data/content';
import classes from './shared.module.css';

export function DeveloperCard() {
  return (
    <section>
      <SectionTitle>Pengembang</SectionTitle>
      <div className={classes.developer}>
        <StripedSurface caption="Foto" className={classes.photo} />
        <div>
          <h3 className={classes.devName}>{DEVELOPER.name}</h3>
          <p className={classes.devMeta}>{DEVELOPER.affiliation}</p>
          <a href={`mailto:${DEVELOPER.email}`} className={classes.devEmail}>
            {DEVELOPER.email}
          </a>
        </div>
      </div>
    </section>
  );
}
