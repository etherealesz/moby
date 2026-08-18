'use client';

import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';
import { IGridRef } from './grid';

interface IGridContextProps<T = any> {
  api: IGridRef<T>['api'] | null;
  grid: IGridRef<T> | null;
  rowData: T[];
  setRowData: React.Dispatch<React.SetStateAction<T[]>>;
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
  totalRow: number;
  setTotalRow: (total: number) => void;
  refresh: () => void;
  updateRows: () => void;
  setApi: (api: any) => void;
}

export const GridContext = createContext<IGridContextProps | undefined>(
  undefined
);

export function useGrid<T>(): IGridContextProps<T> {
  const context = useContext(GridContext);
  if (!context) {
    throw new Error('useGrid must be used inside <GridProvider>');
  }

  return context as IGridContextProps<T>;
}

interface IGridProviderProps<T> {
  children: React.ReactNode;
  gridRef: React.RefObject<IGridRef<T> | null>;
}

export function GridProvider<T>({ children, gridRef }: IGridProviderProps<T>) {
  const [api, setApi] = useState<IGridRef<T>['api'] | null>(null);
  const [grid, setGrid] = useState<IGridRef<T> | null>(null);
  const [rowData, setRowData] = useState<T[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [totalRow, setTotalRow] = useState(0);

  useEffect(() => {
    if (gridRef?.current && grid !== gridRef.current) {
      setGrid(gridRef.current);
    }
  }, [gridRef?.current, grid]);

  const refresh = useCallback(() => {
    grid?.refresh?.();
  }, [grid]);

  const updateRows = useCallback(() => {
    if (!grid?.getCurrentPageRows) {
      return;
    }

    const rows = grid.getCurrentPageRows() ?? [];
    setRowData([...rows]);
  }, [grid]);

  useEffect(() => {
    if (!api) {
      return;
    }

    const listener = () => updateRows();

    api.addEventListener('rowDataUpdated', listener);
    api.addEventListener('modelUpdated', listener);
    api.addEventListener('viewportChanged', listener);

    return () => {
      api.removeEventListener('rowDataUpdated', listener);
      api.removeEventListener('modelUpdated', listener);
      api.removeEventListener('viewportChanged', listener);
    };
  }, [api, updateRows]);

  const value = useMemo(
    () => ({
      api,
      grid,
      setApi,
      rowData,
      setRowData,
      isLoading,
      setIsLoading,
      totalRow,
      setTotalRow,
      refresh,
      updateRows,
    }),
    [api, grid, rowData, isLoading, totalRow]
  );

  return <GridContext.Provider value={value}>{children}</GridContext.Provider>;
}
