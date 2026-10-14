import { MobileTopBar } from '@/app/_components/layout/mobile-top-bar';
import { PageFrame } from '@/app/_components/layout/page-frame';
import { Eyebrow, SectionTitle } from '@/app/_components/ui/text';
import { SYSTEM_FLOW } from '@/app/_data/content';
import { ABOUT_SUMMARY_MOBILE, ABOUT_TITLE_SHORT } from '../content';
import { DeveloperCard } from '../shared/developer-card';
import { FlowStep } from '../shared/flow-step';
import { TechList } from '../shared/tech-list';
import classes from './mobile.module.css';

export function TentangMobile() {
  return (
    <PageFrame header={<MobileTopBar title="Tentang" backHref="/" />}>
      <section className={classes.section}>
        <Eyebrow>Latar belakang</Eyebrow>
        <h1 className={classes.headline}>{ABOUT_TITLE_SHORT}</h1>
        <p className={classes.paragraph}>{ABOUT_SUMMARY_MOBILE}</p>
      </section>
      <div className={classes.section}>
        <TechList />
      </div>
      <section className={classes.section}>
        <SectionTitle>Alur sistem</SectionTitle>
        <ol className={classes.flowList}>
          {SYSTEM_FLOW.map((step, index) => (
            <FlowStep
              key={step.title}
              index={index}
              title={step.title}
              body={step.body}
              last={index === SYSTEM_FLOW.length - 1}
              className={classes.flowCell}
            />
          ))}
        </ol>
      </section>
      <div className={classes.section}>
        <DeveloperCard />
      </div>
    </PageFrame>
  );
}
