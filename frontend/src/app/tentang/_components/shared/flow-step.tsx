import clsx from 'clsx';
import { formatIndex } from '@/app/_components/ui/detection-overlay';
import classes from './shared.module.css';

interface IFlowStepProps {
  index: number;
  title: string;
  body: string;
  last?: boolean;
  className?: string;
}

export function FlowStep({
  index,
  title,
  body,
  last,
  className,
}: IFlowStepProps) {
  return (
    <li className={clsx(className, last && classes.flowLast)}>
      <span className={classes.flowIndex}>{formatIndex(index)}</span>
      <h3 className={classes.flowTitle}>{title}</h3>
      <p className={classes.flowBody}>{body}</p>
    </li>
  );
}
