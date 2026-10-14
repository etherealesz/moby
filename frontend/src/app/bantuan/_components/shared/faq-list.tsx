import { HELP_FAQ } from '@/app/_data/content';
import classes from './shared.module.css';

export function FaqList() {
  return (
    <ul className={classes.faq}>
      {HELP_FAQ.map((item) => (
        <li key={item.question}>
          <details className={classes.faqItem}>
            <summary className={classes.faqQuestion}>{item.question}</summary>
            <p className={classes.faqAnswer}>{item.answer}</p>
          </details>
        </li>
      ))}
    </ul>
  );
}
