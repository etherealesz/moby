'use client';

import { useRef } from 'react';
import { ColDef, IServerSideGetRowsRequest } from 'ag-grid-enterprise';
import {
  AppShell,
  Badge,
  Button,
  Container,
  Rating,
  Stack,
  Title,
} from '@mantine/core';
import {
  CardBodyGrid,
  CardHorizontal,
  CardVertical,
  ResponsiveCardGrid,
} from '@/src/app/_components/table-card/card-variant';
import {
  GridComponent,
  IGridRef,
} from '@/src/app/_components/table-card/grid/grid';
import { GridProvider } from '@/src/app/_components/table-card/grid/grid-context';
import TableCardWrapper from '@/src/app/_components/table-card/wrapper/card-table-wrapper';

export default function TableCardExamplePage() {
  const gridRef = useRef<IGridRef>(null);

  const serverUrl = `${process.env.NEXT_PUBLIC_HEALTHCARE_INTELLIGENCE_API_BASE_URL}/marketplace/get-marketplace-service`;

  interface IMarketplaceService {
    bpis_id: number;
    individual_id: number;
    doctor_image: string;
    service_name: string;
    first_name: string;
    last_name: string;
    is_umum: boolean;
    is_asuransi: boolean;
    is_bpjs: boolean;
    is_online: boolean;
    is_offline: boolean;
    is_home_care: boolean;
    outlet_name: string;
    min_price: string;
    max_price: string;
    count: number;
    doctor_name: string;
    price: string;
  }

  const colDefs: ColDef[] = [
    {
      field: 'id',
      headerName: 'ID',
      filter: 'agTextColumnFilter',
    },
    { field: 'doctor_name', headerName: 'Name', filter: 'agTextColumnFilter' },
    {
      field: 'service_name',
      headerName: 'Service Name',
      filter: 'agTextColumnFilter',
    },
  ];

  const createRequestData = (params: IServerSideGetRowsRequest) => {
    const payload = {
      grid: params,
    };

    return payload;
  };

  return (
    <AppShell padding="lg">
      <AppShell.Main>
        <Stack gap="lg">
          <Title>Table Card Example</Title>

          <GridProvider<IMarketplaceService> gridRef={gridRef}>
            <TableCardWrapper<IMarketplaceService> columns={colDefs}>
              <GridComponent
                ref={gridRef}
                columns={colDefs}
                serverUrl={serverUrl}
                rowModelType="serverSide"
                createRequestData={createRequestData}
              />
              <TableCardWrapper.Card />
            </TableCardWrapper>
          </GridProvider>

          <Container p={0} m={0}>
            <Title mb="md" fw="bold">
              Radio Button
            </Title>
            <ResponsiveCardGrid>
              <CardVertical
                withRadio
                radioValue="option1"
                radioSelected
                image="https://placehold.co/300x200?text=Radio+1"
                title="Radio Option 1"
                subtitle="Selected"
                body={
                  <CardBodyGrid items={[{ label: 'Type', value: 'Premium' }]} />
                }
              />
              <CardVertical
                withRadio
                radioValue="option2"
                radioSelected={false}
                image="https://placehold.co/300x200?text=Radio+2"
                title="Radio Option 2"
                subtitle="Unselected"
                body={
                  <CardBodyGrid
                    items={[{ label: 'Type', value: 'Standard' }]}
                  />
                }
              />
            </ResponsiveCardGrid>
          </Container>

          <Container p={0} m={0} w="24rem">
            <Title mb="md">New Features Test</Title>
            <CardHorizontal
              withCheckbox
              withContextMenu
              image={[['https://placehold.co/90x90?text=Image']]}
              title="New Feature Card"
              subtitle="Testing Checkbox & Menu"
              lowerBody="lower body"
              body={[
                ['ini body', 'QQQ'],
                ['WW', 'RR'],
              ]}
              tags={['Tag1', 'Tag2']}
              bottomActionButton={['View Details', 'Book Now']}
              bottomLeftActionButton={[
                [
                  <Button
                    variant="outline"
                    size="xs"
                    className="flex-1 sm:flex-none"
                  >
                    QQQ
                  </Button>,
                  'Book Now',
                ],
              ]}
              bottomRightActionButton={[['Q', 'B']]}
              contextMenu={
                <>
                  <Button variant="subtle" size="xs" fullWidth justify="start">
                    Edit
                  </Button>
                  <Button
                    variant="subtle"
                    size="xs"
                    fullWidth
                    justify="start"
                    color="red"
                  >
                    Delete
                  </Button>
                </>
              }
              label={[
                <Badge color="red" variant="light" size="sm">
                  Online
                </Badge>,
                'NEW',
              ]}
              status={[<Rating value={5} />]}
              rating={<Rating defaultValue={2} readOnly />}
            />
          </Container>
        </Stack>
      </AppShell.Main>
    </AppShell>
  );
}
