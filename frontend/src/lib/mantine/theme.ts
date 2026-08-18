import { Nunito_Sans } from 'next/font/google';
import { createTheme } from '@mantine/core';

const nunitoSans = Nunito_Sans({
  subsets: ['latin'],
});

const theme = createTheme({
  primaryColor: 'brand',
  primaryShade: 5,
  defaultRadius: 'md',
  fontFamily: nunitoSans.style.fontFamily,
  breakpoints: {
    xs: '36em',
    sm: '48em',
    md: '62em',
    lg: '75em',
    xl: '88em',
  },
  colors: {
    brand: [
      '#67a7ad',
      '#4e99a0',
      '#358a92',
      '#1b7c85',
      '#026D77',
      '#02626b',
      '#02575f',
      '#02575f',
      '#014c53',
      '#014147',
    ],
  },
});

export default theme;
