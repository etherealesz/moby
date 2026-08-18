'use client';

import { LuLocate } from 'react-icons/lu';
import { ActionIcon, Group, Loader, Paper, Text, Tooltip } from '@mantine/core';
import { PRIMARY } from '@/lib/constants/colors';

interface IGpsStatusBannerProps {
  gpsLoading: boolean;
  startLat: string;
  onRefreshGps: () => void;
}

export function GpsStatusBanner({
  gpsLoading,
  startLat,
  onRefreshGps,
}: IGpsStatusBannerProps) {
  return (
    <Paper
      p="xs"
      radius="md"
      style={{
        backgroundColor: gpsLoading ? '#e0f4f6' : '#f0fbfb',
        border: `1px solid ${PRIMARY[200]}`,
      }}
    >
      <Group gap={8} align="center">
        {gpsLoading ? (
          <Loader size="xs" color="brand" />
        ) : (
          <LuLocate size={16} color={PRIMARY[500]} />
        )}
        <Text
          size="xs"
          style={{ color: PRIMARY[700], fontWeight: 600, flex: 1 }}
        >
          {gpsLoading
            ? 'Mendeteksi lokasi GPS…'
            : startLat
              ? '📍 Lokasi terdeteksi'
              : 'Izinkan lokasi untuk auto-detect'}
        </Text>
        {!gpsLoading && (
          <Tooltip label="Refresh lokasi GPS" withArrow>
            <ActionIcon
              size="sm"
              variant="light"
              color="brand"
              onClick={onRefreshGps}
            >
              <LuLocate size={13} />
            </ActionIcon>
          </Tooltip>
        )}
      </Group>
    </Paper>
  );
}
