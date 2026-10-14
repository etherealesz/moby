import type { ReactNode } from 'react';
import clsx from 'clsx';
import { CategorySwatch } from '@/app/_components/ui/category-swatch';
import { WASTE_CATEGORIES } from '@/app/_data/categories';
import { HELP_MAP_LEGEND, HELP_READING } from '@/app/_data/content';
import classes from './shared.module.css';

interface IPairItem {
  key: string;
  mark?: ReactNode;
  title: string;
  body: string;
}

function PairList({ items }: { items: IPairItem[] }) {
  return (
    <ul className={classes.pairs}>
      {items.map((item) => (
        <li
          key={item.key}
          className={clsx(classes.pair, !item.mark && classes.pairNoMark)}
        >
          {item.mark}
          <div>
            <h3 className={classes.pairTitle}>{item.title}</h3>
            <p className={classes.pairBody}>{item.body}</p>
          </div>
        </li>
      ))}
    </ul>
  );
}

export function MapLegend() {
  return (
    <PairList
      items={HELP_MAP_LEGEND.map((item) => ({
        key: item.title,
        title: item.title,
        body: item.body,
        mark:
          item.mark === 'line' ? (
            <span className={classes.markLine} aria-hidden />
          ) : (
            <span
              className={clsx(
                classes.mark,
                item.tone === 'green' ? classes.markGreen : classes.markInk
              )}
              aria-hidden
            >
              {item.mark}
            </span>
          ),
      }))}
    />
  );
}

export function ReadingGuide() {
  return (
    <PairList
      items={HELP_READING.map((item) => ({
        key: item.term,
        title: item.term,
        body: item.body,
      }))}
    />
  );
}

export function CategoryGuide() {
  return (
    <PairList
      items={WASTE_CATEGORIES.map((category) => ({
        key: category.name,
        title: category.name,
        body: `${category.subcategories.join(', ')}. Dibawa ke ${category.facilityTypes.join(' atau ')}.`,
        mark: <CategorySwatch tone={category.tone} />,
      }))}
    />
  );
}
