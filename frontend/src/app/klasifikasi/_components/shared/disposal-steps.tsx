import { formatIndex } from '@/app/_components/ui/detection-overlay';
import { SectionTitle } from '@/app/_components/ui/text';
import type { ClassificationSession } from '../../_hooks/use-classification-session';
import classes from './shared.module.css';

type IDisposalStepsProps = Pick<
  ClassificationSession,
  'selectedCategory' | 'selectedIndex' | 'isConfident'
>;

export function DisposalSteps({
  selectedCategory,
  selectedIndex,
  isConfident,
}: IDisposalStepsProps) {
  if (!selectedCategory) {
    return null;
  }

  return (
    <section className={classes.disposal}>
      <SectionTitle>
        Cara membuang — objek {formatIndex(selectedIndex)}
      </SectionTitle>
      {isConfident ? (
        <ol className={classes.steps}>
          {selectedCategory.disposalSteps.map((step) => (
            <li key={step}>{step}</li>
          ))}
        </ol>
      ) : (
        <p className={classes.note}>
          Keyakinan masih di bawah ambang. Dekatkan objek ke kamera dan tahan
          beberapa saat sampai label stabil.
        </p>
      )}
    </section>
  );
}
