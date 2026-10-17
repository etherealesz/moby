import { Group, Radio } from '@mantine/core';
import { MutedLabel } from '@/app/_components/ui/text';
import type { NetworkType } from '@/app/_models/moby';
import { NETWORK_LABEL } from '@/app/_utils/format';

const MODES: NetworkType[] = ['walk', 'drive'];

interface IModePickerProps {
  value: NetworkType;
  onChange: (value: NetworkType) => void;
}

export function ModePicker({ value, onChange }: IModePickerProps) {
  return (
    <Radio.Group
      value={value}
      onChange={(next) => onChange(next as NetworkType)}
      label={<MutedLabel>Mode perjalanan</MutedLabel>}
    >
      <Group gap={28} mt={12}>
        {MODES.map((mode) => (
          <Radio
            key={mode}
            value={mode}
            label={NETWORK_LABEL[mode]}
            size="sm"
          />
        ))}
      </Group>
    </Radio.Group>
  );
}
