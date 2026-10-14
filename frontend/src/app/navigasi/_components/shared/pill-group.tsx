import clsx from 'clsx';
import classes from './shared.module.css';

interface IPillOption<T> {
  value: T;
  label: string;
}

interface IPillGroupProps<T> {
  label: string;
  options: IPillOption<T>[];
  value: T | null;
  onChange: (value: T) => void;
}

export function PillGroup<T extends string | number>({
  label,
  options,
  value,
  onChange,
}: IPillGroupProps<T>) {
  return (
    <div className={classes.pills} role="group" aria-label={label}>
      {options.map((option) => (
        <button
          key={option.value}
          type="button"
          aria-pressed={option.value === value}
          onClick={() => onChange(option.value)}
          className={clsx(
            classes.pill,
            option.value === value && classes.pillActive
          )}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
}
