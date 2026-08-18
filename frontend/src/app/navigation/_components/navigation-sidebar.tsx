'use client';

import { AppShell, Divider, ScrollArea, Stack } from '@mantine/core';
import { useRouteNavigation } from '../_hooks/useRouteNavigation';
import { ClickModeSelector } from './click-mode-selector';
import { GpsStatusBanner } from './gps-status-banner';
import { RouteForm } from './route-form';
import { RouteResultCard } from './route-result-card';

interface INavigationSidebarProps {
  navState: ReturnType<typeof useRouteNavigation>;
}

export function NavigationSidebar({ navState }: INavigationSidebarProps) {
  const {
    startLat,
    setStartLat,
    startLon,
    setStartLon,
    endLat,
    setEndLat,
    endLon,
    setEndLon,
    mode,
    setMode,
    clickAction,
    setClickAction,
    handleRefreshGps,
    handleCalculateRoute,
    handleReset,
    gpsLoading,
    isRouteLoading,
    errorMessage,
    routeResult,
  } = navState;

  return (
    <AppShell.Navbar
      style={{
        backgroundColor: '#ffffff',
        borderRight: '1px solid #dbeceb',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        boxShadow: '2px 0 12px rgba(2, 109, 119, 0.05)',
        zIndex: 200,
      }}
    >
      <ScrollArea style={{ flex: 1 }} p="md" type="scroll">
        <Stack gap="md">
          {/* GPS Status Banner */}
          <GpsStatusBanner
            gpsLoading={gpsLoading}
            startLat={startLat}
            onRefreshGps={handleRefreshGps}
          />

          <Divider color="#e0f4f6" />

          {/* Click Pin Mode Selector */}
          <ClickModeSelector
            clickAction={clickAction}
            onChange={setClickAction}
          />

          <Divider color="#e0f4f6" />

          {/* Coordinate Form */}
          <RouteForm
            startLat={startLat}
            setStartLat={setStartLat}
            startLon={startLon}
            setStartLon={setStartLon}
            endLat={endLat}
            setEndLat={setEndLat}
            endLon={endLon}
            setEndLon={setEndLon}
            mode={mode}
            setMode={setMode}
            onSubmit={handleCalculateRoute}
            onRefreshGps={handleRefreshGps}
            onReset={handleReset}
            isLoading={isRouteLoading}
            errorMessage={errorMessage}
            hasResult={Boolean(routeResult)}
          />
        </Stack>
      </ScrollArea>

      {/* Result Card */}
      {routeResult && <RouteResultCard result={routeResult} />}
    </AppShell.Navbar>
  );
}
