import React from 'react';
import clsx from 'clsx';
import { Text } from '@mantine/core';

export interface ICardBodyGridItem {
  readonly label: React.ReactNode;
  readonly value: React.ReactNode;
}

export interface ICardBodyGridProps {
  readonly items: ICardBodyGridItem[];
  readonly columnCount?: number;
  readonly className?: string;
}

export default function CardBodyGrid({
  items,
  columnCount = 2,
  className = '',
}: ICardBodyGridProps) {
  return (
    <div
      className={clsx('mt-1 grid gap-1', className)}
      style={{ gridTemplateColumns: `repeat(${columnCount}, minmax(0, 1fr))` }}
    >
      {items.map((item, index) => (
        <div key={index} className="flex flex-col">
          <Text size="xs" c="dimmed" className="mb-1 leading-none">
            {item.label}
          </Text>
          <div className="text-xs leading-tight font-medium wrap-break-word">
            {item.value}
          </div>
        </div>
      ))}
    </div>
  );
}
