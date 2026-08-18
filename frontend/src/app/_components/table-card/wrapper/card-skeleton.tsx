import clsx from 'clsx';
import { Card, Skeleton, Stack } from '@mantine/core';

interface CardSkeletonGridProps {
  readonly cardCount?: number;
  readonly cardMinWidth?: number;
  readonly className?: string;
}

export default function CardSkeleton({
  cardCount = 8,
  cardMinWidth = 250,
  className,
}: CardSkeletonGridProps) {
  return (
    <div
      className={clsx('grid w-full gap-3 p-2', className)}
      style={{
        gridTemplateColumns: `repeat(auto-fill, minmax(${cardMinWidth}px, 1fr))`,
      }}
    >
      {Array.from({ length: cardCount }).map((_, idx) => (
        <Card
          key={idx}
          shadow="sm"
          padding="lg"
          radius="md"
          withBorder
          className="w-full"
        >
          <Stack>
            {/* Avatar or circular image */}
            <Skeleton height={50} circle mb="xl" />

            {/* Title */}
            <Skeleton height={16} radius="sm" />

            {/* Subtitle or text lines */}
            <Skeleton height={12} mt={6} radius="sm" />
            <Skeleton height={12} mt={6} width="70%" radius="sm" />
          </Stack>
        </Card>
      ))}
    </div>
  );
}
