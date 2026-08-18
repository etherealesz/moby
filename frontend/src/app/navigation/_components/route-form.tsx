'use client';

import {
  LuFlag,
  LuInfo,
  LuLocate,
  LuMapPin,
  LuNavigation,
  LuRefreshCw,
} from 'react-icons/lu';
import {
  ActionIcon,
  Alert,
  Button,
  Group,
  Select,
  Stack,
  Text,
  TextInput,
  Tooltip,
} from '@mantine/core';
import { PRIMARY, SEMANTIC } from '@/lib/constants/colors';

interface IRouteFormProps {
  startLat: string;
  setStartLat: (val: string) => void;
  startLon: string;
  setStartLon: (val: string) => void;
  endLat: string;
  setEndLat: (val: string) => void;
  endLon: string;
  setEndLon: (val: string) => void;
  mode: 'walk' | 'drive';
  setMode: (val: 'walk' | 'drive') => void;
  onSubmit: (e: React.FormEvent) => void;
  onRefreshGps: () => void;
  onReset: () => void;
  isLoading: boolean;
  errorMessage: string | null;
  hasResult: boolean;
}

export function RouteForm({
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
  onSubmit,
  onRefreshGps,
  onReset,
  isLoading,
  errorMessage,
  hasResult,
}: IRouteFormProps) {
  return (
    <form onSubmit={onSubmit}>
      <Stack gap="sm">
        {/* Start Coordinates */}
        <div>
          <Group justify="space-between" align="center" mb={4}>
            <Group gap={5}>
              <LuMapPin size={14} color={PRIMARY[500]} />
              <Text
                size="xs"
                fw={700}
                style={{
                  color: PRIMARY[700],
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em',
                }}
              >
                Titik Awal (Penjemputan)
              </Text>
            </Group>
            <Tooltip label="Gunakan koordinat GPS saat ini" withArrow>
              <ActionIcon
                size="xs"
                variant="subtle"
                color="brand"
                onClick={onRefreshGps}
              >
                <LuLocate size={13} />
              </ActionIcon>
            </Tooltip>
          </Group>
          <Group gap="xs" grow>
            <TextInput
              placeholder="Latitude"
              value={startLat}
              onChange={(e) => setStartLat(e.currentTarget.value)}
              required
              size="xs"
              styles={{ input: { borderColor: '#dbeceb', fontSize: 12 } }}
            />
            <TextInput
              placeholder="Longitude"
              value={startLon}
              onChange={(e) => setStartLon(e.currentTarget.value)}
              required
              size="xs"
              styles={{ input: { borderColor: '#dbeceb', fontSize: 12 } }}
            />
          </Group>
        </div>

        {/* End Coordinates */}
        <div>
          <Group gap={5} mb={4}>
            <LuFlag size={14} color={SEMANTIC.danger} />
            <Text
              size="xs"
              fw={700}
              style={{
                color: SEMANTIC.danger,
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
              }}
            >
              Titik Tujuan (TPS / Bank Sampah)
            </Text>
          </Group>
          <Group gap="xs" grow>
            <TextInput
              placeholder="Latitude"
              value={endLat}
              onChange={(e) => setEndLat(e.currentTarget.value)}
              required
              size="xs"
              styles={{ input: { borderColor: '#ffd5cc', fontSize: 12 } }}
            />
            <TextInput
              placeholder="Longitude"
              value={endLon}
              onChange={(e) => setEndLon(e.currentTarget.value)}
              required
              size="xs"
              styles={{ input: { borderColor: '#ffd5cc', fontSize: 12 } }}
            />
          </Group>
        </div>

        {/* Travel Mode Select */}
        <Select
          label="Mode Perjalanan"
          size="xs"
          value={mode}
          onChange={(v) => setMode((v as 'walk' | 'drive') || 'walk')}
          data={[
            { value: 'walk', label: '🚶 Pejalan Kaki' },
            { value: 'drive', label: '🚛 Armada Kendaraan' },
          ]}
          styles={{
            input: { borderColor: '#dbeceb', fontSize: 12 },
            label: {
              color: PRIMARY[700],
              fontSize: 11,
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              marginBottom: 4,
            },
          }}
        />

        {/* Error Alert */}
        {errorMessage && (
          <Alert
            icon={<LuInfo size={14} />}
            title="Perhatian"
            color="red"
            variant="light"
            py="xs"
          >
            {errorMessage}
          </Alert>
        )}

        {/* Actions */}
        <Group gap="xs" mt="xs">
          <Button
            type="submit"
            loading={isLoading}
            color="brand"
            leftSection={<LuNavigation size={14} />}
            flex={1}
            size="sm"
            style={{
              backgroundColor: PRIMARY[500],
              fontWeight: 700,
              boxShadow: '0 4px 12px rgba(2, 109, 119, 0.25)',
            }}
          >
            Hitung Rute Navigasi
          </Button>
          {hasResult && (
            <Tooltip label="Reset rute" withArrow>
              <ActionIcon
                size="lg"
                variant="outline"
                color="brand"
                onClick={onReset}
                style={{ borderColor: '#dbeceb' }}
              >
                <LuRefreshCw size={14} />
              </ActionIcon>
            </Tooltip>
          )}
        </Group>
      </Stack>
    </form>
  );
}
