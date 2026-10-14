import { HELP_STEPS } from '@/app/_data/content';
import classes from './shared.module.css';

export function HelpSteps({ layout }: { layout: 'grid' | 'list' }) {
  return (
    <ol className={layout === 'grid' ? classes.stepsGrid : classes.stepsList}>
      {HELP_STEPS.map((step, index) => (
        <li key={step.title}>
          <span className={classes.stepNumber}>{index + 1}</span>
          <div>
            <h3 className={classes.stepTitle}>{step.title}</h3>
            <p className={classes.stepBody}>{step.body}</p>
          </div>
        </li>
      ))}
    </ol>
  );
}
