import { createTheme } from '@mantine/core';
import { archivo } from './fonts';

const theme = createTheme({
  primaryColor: 'brand',
  primaryShade: 7,
  defaultRadius: 0,
  fontFamily: `${archivo.style.fontFamily}, system-ui, sans-serif`,
  headings: {
    fontFamily: `${archivo.style.fontFamily}, system-ui, sans-serif`,
    fontWeight: '800',
  },
  breakpoints: {
    xs: '36em',
    sm: '48em',
    md: '62em',
    lg: '75em',
    xl: '88em',
  },
  colors: {
    brand: [
      '#eaf3ed',
      '#d3e6da',
      '#a6ccb3',
      '#76b08a',
      '#4f9868',
      '#368a54',
      '#2b7a47',
      '#276b3f',
      '#1d5130',
      '#164326',
    ],
  },
});

export default theme;
