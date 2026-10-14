import Link from 'next/link';
import layoutClasses from '@/app/_components/layout/layout.module.css';
import { MobileMenu } from '@/app/_components/layout/mobile-menu';
import { PageFrame } from '@/app/_components/layout/page-frame';
import { Stat } from '@/app/_components/ui/stat';
import { SUBCATEGORY_COUNT, WASTE_CATEGORIES } from '@/app/_data/categories';
import { CategoryGrid } from './category-grid';
import { MobileHero } from './mobile-hero';
import classes from './mobile.module.css';

export function BerandaMobile() {
  return (
    <PageFrame
      header={
        <header className={layoutClasses.topBar}>
          <Link href="/" className={layoutClasses.topBarLogo}>
            MOBY
          </Link>
          <MobileMenu active="/" />
        </header>
      }
    >
      <MobileHero />
      <div className={classes.stats}>
        <Stat value={WASTE_CATEGORIES.length} label="Kategori" />
        <Stat value={SUBCATEGORY_COUNT} label="Subkategori" />
      </div>
      <CategoryGrid />
    </PageFrame>
  );
}
