'use client';

import { useState, type FormEvent } from 'react';
import clsx from 'clsx';
import { HELP_FAQ, HELP_SECTIONS } from '@/app/_data/content';
import classes from './shared.module.css';

interface IHelpSearchProps {
  idPrefix: string;
  className?: string;
}

function findSectionId(query: string) {
  const q = query.trim().toLowerCase();
  if (!q) {
    return null;
  }
  const section = HELP_SECTIONS.find((item) =>
    `${item.label} ${item.keywords}`.toLowerCase().includes(q)
  );
  if (section) {
    return section.id;
  }
  const inFaq = HELP_FAQ.some((item) =>
    `${item.question} ${item.answer}`.toLowerCase().includes(q)
  );
  return inFaq ? 'masalah' : null;
}

export function HelpSearch({ idPrefix, className }: IHelpSearchProps) {
  const [query, setQuery] = useState('');
  const [missed, setMissed] = useState(false);

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    const id = findSectionId(query);
    setMissed(!id);
    if (id) {
      document
        .getElementById(`${idPrefix}${id}`)
        ?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  return (
    <form role="search" onSubmit={handleSubmit} className={clsx(className)}>
      <input
        type="search"
        value={query}
        onChange={(event) => {
          setQuery(event.target.value);
          setMissed(false);
        }}
        placeholder="Cari panduan"
        aria-label="Cari panduan"
        className={classes.search}
      />
      {missed && (
        <p className={classes.searchMiss}>Tidak ada panduan yang cocok.</p>
      )}
    </form>
  );
}
