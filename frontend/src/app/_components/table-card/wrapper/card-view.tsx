import React from 'react';
import { IconDatabaseOff } from '@tabler/icons-react';
import { ColDef } from 'ag-grid-enterprise';
import clsx from 'clsx';
import { Card, Text } from '@mantine/core';
import { ResponsiveCardGrid } from '../card-variant';

interface ICardViewProps<T> {
  readonly columns: ColDef[];
  readonly data: T[];
  readonly cardChild?: React.ReactElement<{
    readonly onRenderRow?: (
      value: T,
      index: number,
      array: T[]
    ) => React.ReactNode;
    readonly className?: string;
  }>;
  readonly containerClassName?: string;
  readonly cardClassName?: string;
  readonly cardMinWidth?: number;
}

export default function CardView<T>({
  data,
  columns,
  cardChild,
  containerClassName,
  cardClassName,
  cardMinWidth = 250,
}: ICardViewProps<T>) {
  // If no cardChild is provided, we can't render anything custom,
  // but we might want to render a default card view if data exists.
  // However, the previous logic required cardChild to be present.
  // Let's keep it optional but if present, check for onRenderRow.

  const onRenderRow = cardChild?.props?.onRenderRow;

  return (
    <div className={clsx('h-50vh w-full overflow-y-auto', containerClassName)}>
      <div
        className={clsx('grid w-full gap-4 p-2', cardClassName)}
        style={{
          gridTemplateColumns: `repeat(auto-fill, minmax(${cardMinWidth}px, 1fr))`,
        }}
      >
        {data.length === 0 && (
          <div className="col-span-full flex items-center justify-center py-12">
            <div className="flex flex-col items-center gap-3 text-center">
              <div className="rounded-full bg-gray-50 p-3">
                <IconDatabaseOff
                  size={48}
                  className="text-gray-300"
                  stroke={1.5}
                />
              </div>
              <div>
                <Text size="lg" fw={600} c="gray.7">
                  Tidak ada data tersedia
                </Text>
                <Text size="sm" c="dimmed" className="mx-auto mt-1 max-w-xs">
                  Tidak dapat menemukan item yang sesuai dengan kriteria Anda.
                  Coba sesuaikan filter atau istilah pencarian Anda.
                </Text>
              </div>
            </div>
          </div>
        )}
      </div>
      <ResponsiveCardGrid>
        {data.map((row, index, array) => {
          if (onRenderRow) {
            return (
              <React.Fragment key={index}>
                {onRenderRow(row, index, array)}
              </React.Fragment>
            );
          }

          return (
            <Card
              key={index}
              withBorder
              shadow="sm"
              radius="md"
              className="flex flex-col gap-2"
            >
              <div className="flex flex-wrap gap-x-4 gap-y-2">
                {columns.map((col, cIdx) => {
                  const field = col.field as keyof T;
                  const value = row[field];
                  const header = col.headerName;

                  if (!header) {
                    return null;
                  }

                  return (
                    <div key={cIdx} className="flex flex-col">
                      <Text fw={600} size="xs" c="dimmed" tt="uppercase">
                        {header}
                      </Text>
                      <Text size="sm" className="wrap-break-word">
                        {String(value ?? '-')}
                      </Text>
                    </div>
                  );
                })}
              </div>
            </Card>
          );
        })}
      </ResponsiveCardGrid>
    </div>
  );
}
