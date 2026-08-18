import React from 'react';
import clsx from 'clsx';

interface IResponsiveCardGridProps {
  readonly children: React.ReactNode;
  readonly className?: string;
}

export function ResponsiveCardGrid({
  children,
  className,
}: IResponsiveCardGridProps) {
  let classNameLocal = className;
  const childCount = React.Children.count(children);

  if (childCount === 1) {
    classNameLocal = `${classNameLocal ?? ''} justify-center`.trim();
  }

  return (
    <div
      className={clsx(
        'grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 2xl:grid-cols-8',
        classNameLocal
      )}
    >
      {children}
    </div>
  );
}
