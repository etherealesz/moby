import { CategorySwatch } from '@/app/_components/ui/category-swatch';
import { SectionTitle } from '@/app/_components/ui/text';
import { WASTE_CATEGORIES } from '@/app/_data/categories';
import classes from './mobile.module.css';

export function CategoryGrid() {
  return (
    <section className={classes.section}>
      <SectionTitle className={classes.sectionTitle}>
        Panduan pemilahan
      </SectionTitle>
      <div className={classes.categoryGrid}>
        {WASTE_CATEGORIES.map((category) => (
          <article key={category.id} className={classes.categoryCell}>
            <CategorySwatch tone={category.tone} />
            <h3 className={classes.categoryName}>{category.name}</h3>
            <span className={classes.categoryMeta}>
              {category.subcategories.length} subkategori
            </span>
          </article>
        ))}
      </div>
    </section>
  );
}
