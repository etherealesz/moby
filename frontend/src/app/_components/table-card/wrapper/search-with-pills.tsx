import { useEffect, useState } from 'react';
import { useDebounceFn } from 'ahooks';
import { LuSearch } from 'react-icons/lu';
import { Group, Pill, TextInput } from '@mantine/core';

interface ISearchWithPillsProps {
  onSearchChange?: (values: string[]) => void;
  value?: string;
  onInputChange?: (value: string) => void;
  defaultValue?: string;
  defaultPills?: string[];
}

export default function SearchWithPills({
  onSearchChange,
  value: controlledValue,
  onInputChange,
  defaultValue = '',
  defaultPills = [],
}: ISearchWithPillsProps) {
  const [internalValue, setInternalValue] = useState(defaultValue);
  const [pills, setPills] = useState<string[]>(defaultPills);
  const isControlled = controlledValue !== undefined;
  const value = isControlled ? controlledValue : internalValue;

  // Update value based on controlled/uncontrolled mode
  const updateValueBasedOnMode = (value: string) => {
    if (isControlled) {
      onInputChange?.(value);
    }

    setInternalValue(value);
  };

  const { run: runDebouncedSingleSearch } = useDebounceFn(
    (value: string) => {
      const trimmed = value.trim();

      if (!trimmed) {
        onSearchChange?.([...pills]);
        return;
      }

      onSearchChange?.([...pills, trimmed]);
    },
    { wait: 1000 }
  );

  const addPill = (value: string) => {
    const newValue = value.trim();
    if (!newValue) {
      return;
    }

    setPills((prev) => {
      if (prev.includes(newValue)) {
        return prev;
      }

      const updated = [...prev, newValue];
      onSearchChange?.(updated);
      return updated;
    });

    updateValueBasedOnMode('');
  };

  const onKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && value.trim() !== '') {
      e.preventDefault();
      addPill(value);
    }
  };

  const onInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.currentTarget.value;
    updateValueBasedOnMode(value);
    runDebouncedSingleSearch(value);
  };

  const removePill = (value: string) => {
    const updated = pills.filter((p) => p !== value);
    setPills(updated);
    onSearchChange?.(updated);
  };

  useEffect(() => {
    if (isControlled && controlledValue !== undefined) {
      runDebouncedSingleSearch(controlledValue);
    }
  }, [controlledValue, isControlled]);

  return (
    <div>
      <TextInput
        placeholder="Cari..."
        value={value}
        onInput={onInput}
        onKeyDown={onKeyDown}
        leftSection={<LuSearch size={16} />}
      />

      <Group mt="sm" gap="xs">
        {pills.map((pill) => (
          <Pill key={pill} withRemoveButton onRemove={() => removePill(pill)}>
            {pill}
          </Pill>
        ))}
      </Group>
    </div>
  );
}
