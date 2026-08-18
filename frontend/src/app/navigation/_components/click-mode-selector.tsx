'use client';

import { Box, SegmentedControl, Text } from '@mantine/core';
import { PRIMARY } from '@/lib/constants/colors';

interface IClickModeSelectorProps {
  clickAction: 'start' | 'end';
  onChange: (val: 'start' | 'end') => void;
}

export function ClickModeSelector({
  clickAction,
  onChange,
}: IClickModeSelectorProps) {
  return (
    <Box>
      <Text
        size="xs"
        fw={700}
        mb={6}
        style={{
          color: PRIMARY[700],
          letterSpacing: '0.05em',
          textTransform: 'uppercase',
        }}
      >
        🖱️ Klik Peta Untuk Menentukan Titik
      </Text>
      <SegmentedControl
        fullWidth
        size="xs"
        value={clickAction}
        onChange={(val) => onChange(val as 'start' | 'end')}
        data={[
          { value: 'start', label: '🟢 Titik Awal (A)' },
          { value: 'end', label: '🔴 Titik Tujuan (B)' },
        ]}
        color="brand"
        styles={{
          root: { backgroundColor: '#f0fbfb', border: '1px solid #dbeceb' },
          label: { fontSize: 11, fontWeight: 600 },
        }}
      />
    </Box>
  );
}
