import clsx from 'clsx';
import { CategorySwatch } from '@/app/_components/ui/category-swatch';
import { SectionTitle } from '@/app/_components/ui/text';
import { SUBCATEGORY_COUNT, WASTE_CATEGORIES } from '@/app/_data/categories';
import classes from './desktop.module.css';

export function SortingGuide() {
  return (
    <section className={classes.section}>
      <div className={classes.sectionHead}>
        <SectionTitle>Panduan pemilahan</SectionTitle>
        <span className={classes.sectionNote}>
          Empat kategori, {SUBCATEGORY_COUNT} subkategori
        </span>
      </div>

      <div className={classes.grid4}>
        {WASTE_CATEGORIES.map((category) => (
          <article
            key={category.id}
            className={clsx(classes.cell, classes.guideItem)}
          >
            <h3 className={classes.guideTitle}>
              <CategorySwatch tone={category.tone} />
              {category.name}
            </h3>
            <ul className={classes.guideList}>
              {category.subcategories.map((sub) => (
                <li key={sub}>{sub}</li>
              ))}
            </ul>
          </article>
        ))}
      </div>
    </section>
  );
}
