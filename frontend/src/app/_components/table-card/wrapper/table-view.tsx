import React from 'react';

interface ITableViewProps {
  children?: React.ReactNode;
  className?: string;
}

export default function TableView({ children, className }: ITableViewProps) {
  if (!children) {
    return null;
  }

  return <div className={className}>{children}</div>;
}
