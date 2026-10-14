import clsx from 'clsx';
import classes from './shared.module.css';

interface ICameraStatusProps {
  active: boolean;
  onToggle: () => void;
  compact?: boolean;
}

export function CameraStatus({
  active,
  onToggle,
  compact,
}: ICameraStatusProps) {
  const text = active ? 'Aktif' : 'Mati';

  return (
    <button
      type="button"
      onClick={onToggle}
      aria-pressed={active}
      className={clsx(classes.status, !active && classes.statusOff)}
    >
      {compact ? text : `Kamera ${text.toLowerCase()}`}
    </button>
  );
}
