'use client';

import { useRouter } from 'next/navigation';
import { HttpStatusCode } from 'axios';
import { AppShell, Button } from '@mantine/core';
import { ErrorBody } from './_components/errors/body';
import { ErrorFooter } from './_components/errors/footer';
import { ErrorHeader } from './_components/errors/header';

export default function NotFoundPage() {
  const router = useRouter();

  return (
    <AppShell>
      <AppShell.Header>
        <ErrorHeader
          errorCode={HttpStatusCode.NotFound}
          errorDescription="Halaman Tidak Ditemukan"
        />
      </AppShell.Header>

      <AppShell.Main>
        <ErrorBody
          title="Halaman Tidak Ditemukan"
          description="Maaf, halaman yang Anda cari tidak ada di server kami. Halaman tersebut mungkin telah dihapus, dipindahkan, atau salah."
          image={{
            src: '/images/errors/404.svg',
            alt: '404 Not Found',
          }}
        >
          <ErrorBody.Action>
            <Button onClick={() => router.replace('/')}>
              Kembali ke Beranda
            </Button>
          </ErrorBody.Action>
        </ErrorBody>
      </AppShell.Main>

      <AppShell.Footer>
        <ErrorFooter />
      </AppShell.Footer>
    </AppShell>
  );
}
