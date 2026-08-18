import { Select } from '@mantine/core';
import { TTableCardViewType } from './types';

interface IToggleSelectProps {
  viewType: TTableCardViewType;
  onChange: (value: TTableCardViewType) => void;
}

export default function ToggleSelect({
  viewType,
  onChange,
}: IToggleSelectProps) {
  return (
    <div className="w-full">
      <Select
        placeholder="Pick one"
        data={[
          { value: 'card', label: 'Card' },
          { value: 'table', label: 'Table' },
        ]}
        value={viewType}
        onChange={(value) => onChange(value as TTableCardViewType)}
        className="w-full"
        allowDeselect={false}
      />
    </div>
  );
}
