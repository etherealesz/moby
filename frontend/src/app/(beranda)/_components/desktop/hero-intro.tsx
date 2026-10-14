import { LinkButton } from '@/app/_components/ui/link-button';
import { Stat } from '@/app/_components/ui/stat';
import { Eyebrow } from '@/app/_components/ui/text';
import { SUBCATEGORY_COUNT, WASTE_CATEGORIES } from '@/app/_data/categories';
import { HERO_LEAD, HERO_TITLE } from '../content';
import classes from './desktop.module.css';

export function HeroIntro() {
  return (
    <div className={classes.intro}>
      <Eyebrow>Klasifikasi sampah &amp; rute fasilitas</Eyebrow>
      <h1 className={classes.headline}>
        {HERO_TITLE.map((line) => (
          <span key={line}>{line}</span>
        ))}
      </h1>
      <p className={classes.lead}>{HERO_LEAD}</p>
      <div className={classes.actions}>
        <LinkButton href="/klasifikasi">Buka kamera</LinkButton>
        <LinkButton href="/navigasi" variant="outline">
          Lihat peta rute
        </LinkButton>
      </div>
      <div className={classes.stats}>
        <Stat value={WASTE_CATEGORIES.length} label="Kategori sampah" />
        <Stat value={SUBCATEGORY_COUNT} label="Subkategori sampah" />
      </div>
    </div>
  );
}
