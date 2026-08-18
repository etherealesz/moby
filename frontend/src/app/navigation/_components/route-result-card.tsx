'use client';

import { LuCompass, LuRoute, LuWaypoints } from 'react-icons/lu';
import { Badge, Box, Group, Paper, Stack, Text } from '@mantine/core';
import { PRIMARY } from '@/lib/constants/colors';
import { IRouteResponseData } from '../_models/route';

interface IRouteResultCardProps {
  result: IRouteResponseData;
}

export function RouteResultCard({ result }: IRouteResultCardProps) {
  const estimatedTimeMinutes =
    result.mode === 'walk'
      ? Math.ceil(result.distance_meters / 80)
      : Math.ceil(result.distance_meters / 400);

  return (
    <Box
      p="md"
      style={{
        borderTop: '1px solid #dbeceb',
        backgroundColor: '#f8fdfc',
        flexShrink: 0,
      }}
    >
      <Paper
        p="sm"
        radius="md"
        style={{ backgroundColor: '#ffffff', border: '1px solid #dbeceb' }}
      >
        <Group justify="space-between" align="center" mb="xs">
          <Group gap={5}>
            <LuRoute size={14} color={PRIMARY[500]} />
            <Text
              size="xs"
              fw={700}
              style={{
                color: PRIMARY[700],
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
              }}
            >
              Hasil Rute
            </Text>
          </Group>
          <Badge size="xs" color="teal">
            Optimal
          </Badge>
        </Group>

        <Stack gap={6}>
          <Group justify="space-between">
            <Text size="xs" c="dimmed">
              Jarak Total
            </Text>
            <Text size="sm" fw={700} c="dark">
              {(result.distance_meters / 1000).toFixed(2)} km
              <Text span size="xs" c="dimmed">
                {' '}
                ({Math.round(result.distance_meters)} m)
              </Text>
            </Text>
          </Group>
          <Group justify="space-between">
            <Text size="xs" c="dimmed">
              Mode
            </Text>
            <Badge size="xs" color={result.mode === 'walk' ? 'teal' : 'orange'}>
              {result.mode === 'walk' ? '🚶 Walk' : '🚛 Drive'}
            </Badge>
          </Group>
          <Group justify="space-between">
            <Group gap={4}>
              <LuWaypoints size={12} />
              <Text size="xs" c="dimmed">
                Waypoints
              </Text>
            </Group>
            <Text size="xs" fw={700}>
              {result.route.length}
            </Text>
          </Group>
          <Group justify="space-between">
            <Group gap={4}>
              <LuCompass size={12} />
              <Text size="xs" c="dimmed">
                Estimasi Waktu
              </Text>
            </Group>
            <Text size="xs" fw={700} style={{ color: PRIMARY[500] }}>
              {estimatedTimeMinutes} menit
            </Text>
          </Group>
        </Stack>
      </Paper>
    </Box>
  );
}
