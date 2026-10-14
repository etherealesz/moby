import { Metadata } from 'next';
import { ColorSchemeScript, MantineProvider } from '@mantine/core';
import { ModalsProvider } from '@mantine/modals';
import { Notifications } from '@mantine/notifications';
import { archivo } from '../lib/mantine/fonts';
import theme from '../lib/mantine/theme';

import '../styles/globals.css';

import { SWRConfig } from 'swr';

export const metadata: Metadata = {
  title: {
    default: 'MOBY — Klasifikasi Sampah & Rute Fasilitas',
    template: '%s · MOBY',
  },
  description:
    'MOBY: klasifikasi citra sampah dengan MobileNetV4 dan rute ke fasilitas pengelolaan dengan A* Search.',
  robots: '/robots.txt',
  icons: {
    icon: '/images/logo.png',
  },
};

export default function RootLayout({
  children,
}: Readonly<React.PropsWithChildren>) {
  return (
    <html lang="id" className={archivo.variable} suppressHydrationWarning>
      <head>
        <ColorSchemeScript forceColorScheme="light" />
        {/*<meta
          httpEquiv="Content-Security-Policy"
          content="
            default-src 'self';
            style-src 'self' 'unsafe-inline';
            script-src 'self' 'unsafe-inline' blob:;
            connect-src 'self';
            worker-src 'self' blob:;
            img-src 'self' data: blob:;
            media-src 'self' data: blob:;
            frame-src 'self';
            child-src 'self' blob:;
          "
        />*/}
      </head>
      <body className="antialiased">
        <MantineProvider
          theme={theme}
          forceColorScheme="light"
          defaultColorScheme="light"
        >
          <Notifications position="top-right" zIndex={9999} />
          <ModalsProvider>
            <SWRConfig
              value={{
                revalidateOnFocus: false,
                revalidateOnReconnect: false,
                errorRetryCount: 3,
              }}
            >
              {children}
            </SWRConfig>
          </ModalsProvider>
        </MantineProvider>
      </body>
    </html>
  );
}
