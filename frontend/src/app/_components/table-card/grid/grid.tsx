'use client';

import {
  forwardRef,
  RefObject,
  useCallback,
  useImperativeHandle,
  useMemo,
  useRef,
  useState,
} from 'react';
import {
  AllEnterpriseModule,
  ColDef,
  colorSchemeDark,
  GridReadyEvent,
  IDatasource,
  IServerSideDatasource,
  IServerSideGetRowsParams,
  IServerSideGetRowsRequest,
  ModuleRegistry,
  themeQuartz,
} from 'ag-grid-enterprise';
import { AgGridReact, AgGridReactProps } from 'ag-grid-react';
import { AxiosResponse } from 'axios';
import { useMantineColorScheme } from '@mantine/core';
import { defaultHttpClient } from '@/lib/api/http/client';
import { TStandardResponseGrid } from '@/src/shared/data/schemas/grid';
import { useGrid } from './grid-context';

ModuleRegistry.registerModules([AllEnterpriseModule]);

export interface IGridProps extends AgGridReactProps {
  fetchKey?: string;
  columns?: ColDef[];
  data?: any[];
  serverUrl?: string;
  externalDatasource?: IServerSideDatasource<any> | null;
  createRequestData?: (request: IServerSideGetRowsRequest) => any;
  onResponse?: (response: any) => void;
}

export interface IGridRef<T = any> extends AgGridReact {
  insertRow: (row: any) => void;
  updateRow: (id: string | number, updates: any) => void;
  deleteRow: (id: string | number) => void;
  refresh: () => void;
  getCurrentPageRows: () => T[];
  getAllRows: () => T[];
  dataSource: RefObject<IServerSideDatasource<any> | null> | null;
  setDatasource: (ds: IServerSideDatasource) => void;
  setLoading: (params: boolean) => void;
  isLoading: boolean;
  totalRow: number;
}

export const GridComponent = forwardRef<IGridRef, IGridProps>(
  (
    {
      fetchKey,
      columns,
      data,
      serverUrl,
      datasource,
      createRequestData,
      onResponse,
      ...agGridProps
    },
    ref
  ) => {
    const gridRef = useRef<AgGridReact>(null);
    const datasourceRef = useRef<IServerSideDatasource | null>(null);
    const {
      setIsLoading,
      setApi,
      updateRows,
      isLoading,
      totalRow,
      setTotalRow,
    } = useGrid();
    const { colorScheme } = useMantineColorScheme();

    // Default columns
    const [columnDefs] = useState<ColDef[]>(
      columns ?? [
        { field: 'column-1', minWidth: 220 },
        { field: 'column-2', minWidth: 200 },
        { field: 'column-3' },
        { field: 'column-4', minWidth: 90 },
        { field: 'column-5', minWidth: 100 },
      ]
    );

    const defaultColDef = useMemo<ColDef>(
      () => ({
        flex: 1,
        filter: false,
        suppressHeaderFilterButton: true,
      }),
      []
    );

    const isClientSide = useMemo(() => {
      return agGridProps.rowModelType === 'clientSide';
    }, []);

    const isServerSide = useMemo(() => {
      return agGridProps.rowModelType === 'serverSide';
    }, []);

    const createServerSideDatasource = (
      server: any
    ): IServerSideDatasource => ({
      getRows: (params) => {
        setIsLoading(true);
        const total = 8618;
        setTotalRow(total);
        const response = server.getData(params.request);

        setTimeout(() => {
          response.success
            ? params.success({ rowData: response.rows, rowCount: total })
            : params.fail();
          setIsLoading(false);
          updateRows();
        }, 500);
      },
    });

    const createMockServer = (allData: any[]) => ({
      getData: (request: IServerSideGetRowsRequest) => {
        const requestedRows = allData.slice(request.startRow, request.endRow);
        return { success: true, rows: requestedRows };
      },
    });

    const onGridReady = useCallback(
      (params: GridReadyEvent) => {
        // Only set initial data for client side, while for server side
        // data will be set on datasource
        if (isClientSide) {
          gridRef.current?.api.setGridOption('rowData', data ?? []);
        }

        let datasourceLocal: IDatasource | IServerSideDatasource | undefined =
          datasource;
        let serverUrlLocal = serverUrl;

        setApi(params.api);
        setTotalRow(0);
        setIsLoading(true);

        if (serverUrl != null) {
          datasourceLocal = {
            getRows: async (params: IServerSideGetRowsParams) => {
              const payload = createRequestData
                ? createRequestData(params.request)
                : {
                    grid: params.request,
                  };

              const response = await defaultHttpClient<TStandardResponseGrid>(
                serverUrlLocal!,
                {
                  method: 'POST',
                  data: payload,
                }
              );

              onResponse?.(response);

              if (response.data.data.grid) {
                const total = response.data.data.grid_total ?? 0;
                setTotalRow(total);

                params.success({
                  rowData: response.data.data.grid as any[],
                  rowCount: total,
                });
              } else {
                params.fail();
              }

              setIsLoading(false);
            },
          };
        } else {
          // default datasource
          serverUrlLocal =
            'https://www.ag-grid.com/example-assets/olympic-winners.json';

          // Prepare mock server
          defaultHttpClient(serverUrlLocal).then(
            (response: AxiosResponse<any[]>) => {
              if (isServerSide) {
                const mockServer = createMockServer(response.data);
                datasourceLocal = createServerSideDatasource(mockServer);
              }
            }
          );
        }

        if (
          isServerSide &&
          datasourceLocal !== undefined &&
          datasourceLocal != null
        ) {
          datasourceRef.current = datasourceLocal as IServerSideDatasource;
          params.api!.setGridOption(
            'serverSideDatasource',
            datasourceLocal as IServerSideDatasource
          );
        }
      },
      [serverUrl]
    );

    useImperativeHandle(ref, () => {
      // Create a proxy that forwards all AgGridReact properties dynamically
      const customMethods = {
        get dataSource() {
          return datasourceRef.current;
        },
        get isLoading() {
          return isLoading;
        },
        get totalRow() {
          return totalRow;
        },
        setDatasource: (datasource: IServerSideDatasource) => {
          datasourceRef.current = datasource;
          gridRef.current?.api.setGridOption(
            'serverSideDatasource',
            datasource
          );
        },
        setIsLoading: (param: boolean) => {
          setIsLoading(param);
        },
        insertRow(row: any) {
          gridRef.current?.api.applyTransaction({ add: [row] });
        },
        updateRow(id: string | number, updates: any) {
          gridRef.current?.api.forEachNode((node) => {
            if (node.data?.id === id) {
              Object.assign(node.data, updates);
              gridRef.current?.api.applyTransaction({ update: [node.data] });
            }
          });
        },
        deleteRow(id: string | number) {
          const toRemove: any[] = [];
          gridRef.current?.api.forEachNode((node) => {
            if (node.data?.id === id) {
              toRemove.push(node.data);
            }
          });

          gridRef.current?.api.applyTransaction({ remove: toRemove });
        },
        refresh() {
          gridRef.current?.api.refreshServerSide?.({});
        },
        getCurrentPageRows<T>(): T[] {
          const api = gridRef.current?.api;
          if (!api) {
            return [];
          }

          const modelType = api.getGridOption('rowModelType');
          const pageSize = api.paginationGetPageSize() ?? 1;
          const currentPage = api.paginationGetCurrentPage() ?? 0;
          const startRow = currentPage * pageSize;
          const endRow = startRow + pageSize;
          const rows: T[] = [];

          if (modelType === 'serverSide') {
            const rowsToPush = api
              .getRenderedNodes()
              .map((n: any) => n.data)
              .filter(Boolean);
            rows.push(...rowsToPush);

            return rows;
          }

          if (modelType === 'clientSide') {
            api.forEachNodeAfterFilterAndSort((node: any) => {
              if (node.data) {
                rows.push(node.data);
              }
            });
          }

          return rows.slice(startRow, endRow);
        },
        getAllRows<T>(): T[] {
          const api = gridRef.current?.api;
          if (!api) {
            return [];
          }

          const modelType = api.getGridOption('rowModelType');
          if (modelType !== 'clientSide') {
            throw new Error(`getAllRows only works in 'clientSide'`);
          }

          const rows: T[] = [];
          api.forEachNode((node: any) => {
            if (node.data) {
              rows.push(node.data);
            }
          });

          return rows;
        },
      };

      return new Proxy(customMethods, {
        get(target: any, prop: string | symbol) {
          if (prop in target) {
            return target[prop];
          }

          const gridInstance = gridRef.current as any;
          if (gridInstance && prop in gridInstance) {
            const value = gridInstance[prop];
            return typeof value === 'function'
              ? value.bind(gridInstance)
              : value;
          }

          return undefined;
        },
      }) as IGridRef;
    }, []);

    const theme = useMemo(() => {
      let base = themeQuartz.withParams({
        borderRadius: 4,
        fontSize: 12,
        headerFontSize: 14,
        spacing: 4,
        wrapperBorderRadius: 8,
      });

      const isSystemDark =
        colorScheme === 'auto'
          ? window.matchMedia('(prefers-color-scheme: dark)').matches
          : colorScheme === 'dark';

      if (isSystemDark) {
        base = base.withPart(colorSchemeDark);
      }

      return base;
    }, [colorScheme]);

    return (
      <div className="h-[50vh] w-full overflow-auto">
        <AgGridReact
          theme={theme}
          ref={gridRef}
          rowModelType="serverSide"
          onGridReady={onGridReady}
          columnDefs={columnDefs}
          defaultColDef={defaultColDef}
          pagination
          paginationPageSize={12}
          paginationPageSizeSelector={[10, 20, 50, 100]}
          cacheBlockSize={isServerSide ? 100 : undefined}
          blockLoadDebounceMillis={1000}
          suppressServerSideFullWidthLoadingRow
          enableCellTextSelection
          getContextMenuItems={() => []}
          suppressPaginationPanel
          {...agGridProps}
        />
      </div>
    );
  }
);
