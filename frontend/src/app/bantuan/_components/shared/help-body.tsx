import { Eyebrow } from '@/app/_components/ui/text';
import { HELP_CAMERA_TIPS, HELP_SECTIONS } from '@/app/_data/content';
import { FaqList } from './faq-list';
import { CategoryGuide, MapLegend, ReadingGuide } from './help-pairs';
import { HelpSection } from './help-section';
import { HelpSteps } from './help-steps';
import classes from './shared.module.css';

const LABEL = Object.fromEntries(
  HELP_SECTIONS.map((section) => [section.id, section.label])
) as Record<(typeof HELP_SECTIONS)[number]['id'], string>;

interface IHelpBodyProps {
  idPrefix: string;
  layout: 'desktop' | 'mobile';
}

export function HelpBody({ idPrefix, layout }: IHelpBodyProps) {
  const id = (name: keyof typeof LABEL) => `${idPrefix}${name}`;

  return (
    <div className={classes.body}>
      <section id={id('memulai')} className={classes.section}>
        <Eyebrow>{LABEL.memulai}</Eyebrow>
        <h1 className={classes.title}>Tiga langkah dari kamera ke fasilitas</h1>
        {layout === 'desktop' && (
          <p className={classes.lead}>
            Panduan singkat ini menjelaskan urutan pemakaian modul, arti angka
            pada hasil klasifikasi, dan cara membaca rute pada peta.
          </p>
        )}
        <HelpSteps layout={layout === 'desktop' ? 'grid' : 'list'} />
      </section>

      <HelpSection id={id('kamera')} title={LABEL.kamera}>
        <ul className={classes.tips}>
          {HELP_CAMERA_TIPS.map((tip) => (
            <li key={tip}>{tip}</li>
          ))}
        </ul>
      </HelpSection>

      <HelpSection id={id('hasil')} title={LABEL.hasil}>
        <ReadingGuide />
      </HelpSection>

      <HelpSection id={id('kategori')} title={LABEL.kategori}>
        <CategoryGuide />
      </HelpSection>

      <HelpSection id={id('peta')} title="Arti tanda pada peta">
        <MapLegend />
      </HelpSection>

      <HelpSection id={id('masalah')} title={LABEL.masalah}>
        <FaqList />
      </HelpSection>
    </div>
  );
}
