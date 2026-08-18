'use client';

import React, {
  Activity,
  useCallback,
  useEffect,
  useMemo,
  useState,
} from 'react';
import {
  ColDef,
  IServerSideDatasource,
  IServerSideGetRowsParams,
} from 'ag-grid-enterprise';
import { NumberInput, Pagination, Text } from '@mantine/core';
import { DEFAULT_PAGINATION_PAGE_SIZE } from '@/src/shared/constants/pagination';
import { useGrid } from '../grid/grid-context';
import CardSkeleton from './card-skeleton';
import CardView from './card-view';
import SearchWithPills from './search-with-pills';
import TableView from './table-view';
import ToggleSelect from './toggle-select';
import { TTableCardDisplayName, TTableCardViewType } from './types';

interface ITableCardWrapperProps {
  columns: ColDef[];
  children: React.ReactNode;
  viewMode?: TTableCardViewType;
  hideViewMode?: boolean;
  hideSearch?: boolean;
  searchValue?: string;
  onSearchInputChange?: (value: string) => void;
  defaultSearchValue?: string;
  defaultSearchPills?: string[];
  containerClassName?: string;
  cardMinWidth?: number;
}

interface ICardWrapperProps<T> {
  onRenderRow?: (row: T, index: number, array: T[]) => React.ReactNode;
  className?: string;
  containerClassName?: string;
  minCardWidth?: number;
}

interface ICardSlotProps<T> {
  onRenderRow?: (value: T, index: number, array: T[]) => React.ReactNode;
  displayName?: TTableCardDisplayName;
  className?: string;
}

export default function TableCardWrapper<T>({
  columns,
  children,
  viewMode = 'table',
  hideViewMode = false,
  hideSearch = false,
  searchValue,
  onSearchInputChange,
  defaultSearchValue,
  defaultSearchPills,
  containerClassName,
  cardMinWidth,
}: ITableCardWrapperProps) {
  const { rowData, isLoading, api, updateRows, grid, totalRow } = useGrid<T>();
  const [viewType, setViewType] = useState<TTableCardViewType>(viewMode);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [pageSize, setPageSize] = useState(0);

  const isCard = useMemo(() => viewType === 'card', [viewType]);
  const isTable = useMemo(() => viewType === 'table', [viewType]);

  const tableActivityMode = isTable ? 'visible' : 'hidden';
  const cardActivityMode = isCard ? 'visible' : 'hidden';
  const searchActivityMode = hideSearch ? 'hidden' : 'visible';

  const [pageSizeInput, setPageSizeInput] = useState(
    DEFAULT_PAGINATION_PAGE_SIZE
  );

  const cardChild = React.Children.toArray(children).find((child) => {
    return (
      React.isValidElement(child) &&
      (child.type as any).displayName === 'TableCardWrapper.Card'
    );
  }) as React.ReactElement<ICardWrapperProps<T>> | undefined;

  const tableContent = React.Children.toArray(children).filter((child) => {
    return (
      React.isValidElement(child) &&
      (child.type as any).displayName !== 'TableCardWrapper.Card'
    );
  });

  const updatePaginationState = useCallback(() => {
    if (!api) {
      return;
    }

    setCurrentPage(api.paginationGetCurrentPage() + 1);
    setTotalPages(api.paginationGetTotalPages());
    setPageSize(api.paginationGetPageSize());
  }, [api]);

  useEffect(() => {
    if (!api) {
      return;
    }

    updatePaginationState();
    api.addEventListener('paginationChanged', updatePaginationState);
    api.addEventListener('rowDataUpdated', updateRows);

    return () => {
      api.removeEventListener('paginationChanged', updatePaginationState);
      api.removeEventListener('rowDataUpdated', updateRows);
    };
  }, [api, updatePaginationState, updateRows]);

  const onPageChange = (page: number) => {
    if (!api) {
      return;
    }

    api.paginationGoToPage(page - 1);
    setCurrentPage(page);
  };

  const onPageSizeChange = (value: string) => {
    const numValue = parseInt(value, 10);
    setPageSizeInput(numValue);

    if (!isNaN(numValue) && numValue > 0 && api) {
      api.setGridOption('paginationPageSize', numValue);
    }
  };

  const handleSearchChange = useCallback(
    (keywords: string[]) => {
      if (!api) {
        return;
      }

      const gridType = api.getGridOption('rowModelType');
      if (gridType === 'clientSide') {
        const keyword = keywords.join(' ').trim();
        api.setGridOption('quickFilterText', keyword);
        return;
      }

      if (gridType === 'serverSide' && grid) {
        grid.refresh = () => {
          api.refreshServerSide?.({ purge: true });
        };

        const oldSource = grid?.dataSource as IServerSideDatasource | null;
        if (oldSource && 'getRows' in oldSource) {
          api!.setGridOption('serverSideDatasource', {
            getRows: (params: IServerSideGetRowsParams) => {
              const newRequest = {
                ...params.request,
                universalFilter: keywords,
              };
              oldSource.getRows({ ...params, request: newRequest });
            },
          });

          api.refreshServerSide({ purge: true });
        }

        api.refreshServerSide?.({ purge: true });
      }
    },
    [api, grid]
  );

  useEffect(() => {
    updateRows();
  }, [updateRows]);

  return (
    <div className="w-full space-y-2">
      <div className="flex w-full! items-start gap-2">
        <Activity mode={searchActivityMode}>
          <div className="flex-1">
            <SearchWithPills
              onSearchChange={handleSearchChange}
              value={searchValue}
              onInputChange={onSearchInputChange}
              defaultValue={defaultSearchValue}
              defaultPills={defaultSearchPills}
            />
          </div>
        </Activity>

        {!hideViewMode && (
          <div className="w-24">
            <ToggleSelect viewType={viewType} onChange={setViewType} />
          </div>
        )}
      </div>

      {/* Card View */}
      <Activity mode={cardActivityMode}>
        {!isLoading ? (
          <CardView<T>
            columns={columns}
            data={rowData}
            cardChild={cardChild}
            cardClassName={cardChild?.props?.className}
            containerClassName={
              containerClassName || cardChild?.props?.containerClassName
            }
            cardMinWidth={cardMinWidth || cardChild?.props?.minCardWidth}
          />
        ) : (
          <CardSkeleton />
        )}
      </Activity>

      {/* Table View */}
      <Activity mode={tableActivityMode}>
        <TableView>{tableContent}</TableView>
      </Activity>

      {/* Pagination */}
      <div className="flex w-full flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        {/* Left controls (page size + pagination) */}
        <div className="flex w-full flex-col items-center justify-center gap-3 sm:w-auto sm:flex-row">
          {/* Pagination - mobile first */}
          <div className="order-1 flex w-full justify-center sm:order-2">
            <Pagination
              total={totalPages}
              boundaries={2}
              value={currentPage}
              onChange={onPageChange}
              withEdges
            />
          </div>

          {/* Page size input */}
          <div className="order-2 w-20 sm:order-1">
            <NumberInput
              placeholder="Size"
              value={pageSizeInput}
              onChange={(e) => onPageSizeChange(e.toString())}
              min={1}
            />
          </div>
        </div>

        {/* Total data - always last on mobile */}
        <div className="order-3 sm:order-0">
          <Text>Total Data: {totalRow}</Text>
        </div>
      </div>
    </div>
  );
}

function CardSlot<T>({
  onRenderRow: _onRenderRow,
  className: _className,
}: ICardSlotProps<T>) {
  return null;
}

CardSlot.displayName = 'TableCardWrapper.Card';

TableCardWrapper.Card = CardSlot;
