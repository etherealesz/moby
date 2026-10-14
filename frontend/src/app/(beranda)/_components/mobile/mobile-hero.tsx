import { LinkButton } from '@/app/_components/ui/link-button';
import { Eyebrow } from '@/app/_components/ui/text';
import { HERO_LEAD_SHORT, HERO_TITLE } from '../content';
import classes from './mobile.module.css';

export function MobileHero() {
  return (
    <section className={classes.hero}>
      <Eyebrow>Klasifikasi &amp; rute sampah</Eyebrow>
      <h1 className={classes.headline}>
        {HERO_TITLE.map((line) => (
          <span key={line}>{line}</span>
        ))}
      </h1>
      <p className={classes.lead}>{HERO_LEAD_SHORT}</p>
      <div className={classes.actions}>
        <LinkButton href="/klasifikasi" block>
          Buka kamera
        </LinkButton>
        <LinkButton href="/navigasi" variant="outline" block>
          Lihat peta rute
        </LinkButton>
      </div>
    </section>
  );
}
