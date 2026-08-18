'use client';

import dynamic from 'next/dynamic';
import { AppShell, Box, Loader, Stack, Text } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { PRIMARY } from '@/lib/constants/colors';
import { NavigationHeader } from './_components/navigation-header';
import { NavigationSidebar } from './_components/navigation-sidebar';
import { useRouteNavigation } from './_hooks/useRouteNavigation';

// ── Dynamic Map (SSR disabled) ─────────────────────────────────────────────
const MapView = dynamic(() => import('../_components/Map'), {
  ssr: false,
  loading: () => (
    <Stack
      h="100%"
      align="center"
      justify="center"
      gap="sm"
      style={{ background: '#f8fbfc', borderRadius: 12 }}
    >
      <Loader size="lg" color="brand" />
      <Text size="sm" c="dimmed">
        Memuat peta interaktif…
      </Text>
    </Stack>
  ),
});

export default function NavigationPage() {
  const [opened, { toggle }] = useDisclosure();
  const navState = useRouteNavigation();

  return (
    <AppShell
      header={{ height: 60 }}
      navbar={{
        width: 360,
        breakpoint: 'sm',
        collapsed: { mobile: !opened },
      }}
      styles={{
        main: {
          backgroundColor: '#f4fbfb',
          height: 'calc(100vh - 60px)',
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column',
          padding: '16px',
        },
      }}
    >
      {/* ═══ Header ═══════════════════════════════════════════════════════ */}
      <NavigationHeader opened={opened} onToggle={toggle} />

      {/* ═══ Sidebar ══════════════════════════════════════════════════════ */}
      <NavigationSidebar navState={navState} />

      {/* ═══ Main Content: Map ════════════════════════════════════════════ */}
      <AppShell.Main>
        <Box
          style={{
            width: '100%',
            height: '100%',
            position: 'relative',
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          {/* Top Helper Bar */}
          <Box mb="xs">
            <Text size="xs" fw={600} style={{ color: PRIMARY[700] }}>
              🗺️ Peta Navigasi OpenStreetMap
            </Text>
          </Box>

          {/* Map Framed Container */}
          <Box style={{ flex: 1, position: 'relative', minHeight: 0 }}>
            <MapView
              startCoords={navState.currentStart}
              endCoords={navState.currentEnd}
              routeCoords={navState.routeCoords}
              mode={navState.mode}
              onMapClick={navState.handleMapClick}
            />
          </Box>
        </Box>
      </AppShell.Main>
    </AppShell>
  );
}
