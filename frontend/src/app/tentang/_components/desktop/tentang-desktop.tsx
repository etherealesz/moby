import { DesktopFooter } from '@/app/_components/layout/desktop-footer';
import { DesktopHeader } from '@/app/_components/layout/desktop-header';
import { PageFrame } from '@/app/_components/layout/page-frame';
import { Eyebrow, SectionTitle } from '@/app/_components/ui/text';
import { SYSTEM_FLOW } from '@/app/_data/content';
import { ABOUT_PARAGRAPHS, ABOUT_TITLE } from '../content';
import { DeveloperCard } from '../shared/developer-card';
import { FlowStep } from '../shared/flow-step';
import { TechList } from '../shared/tech-list';
import classes from './desktop.module.css';

export function TentangDesktop() {
  return (
    <PageFrame
      header={<DesktopHeader active="/tentang" subtitle="Tentang" />}
      footer={<DesktopFooter />}
    >
      <div className={classes.top}>
        <section className={classes.background}>
          <Eyebrow>Latar belakang</Eyebrow>
          <h1 className={classes.headline}>{ABOUT_TITLE}</h1>
          {ABOUT_PARAGRAPHS.map((paragraph) => (
            <p key={paragraph} className={classes.paragraph}>
              {paragraph}
            </p>
          ))}
        </section>
        <div className={classes.panel}>
          <TechList />
          <DeveloperCard />
        </div>
      </div>

      <section className={classes.flowSection}>
        <SectionTitle>Alur sistem</SectionTitle>
        <ol className={classes.flowGrid}>
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
    </PageFrame>
  );
}
