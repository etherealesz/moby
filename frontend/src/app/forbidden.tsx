'use client';

import { useRouter } from 'next/navigation';
import { HttpStatusCode } from 'axios';
import { AppShell, Button } from '@mantine/core';
import { ErrorBody } from './_components/errors/body';
import { ErrorFooter } from './_components/errors/footer';
import { ErrorHeader } from './_components/errors/header';

export default function ForbiddenPage() {
  const router = useRouter();

  return (
    <AppShell>
      <AppShell.Header>
        <ErrorHeader
          errorCode={HttpStatusCode.Forbidden}
          errorDescription="Akses Ditolak"
        />
      </AppShell.Header>

      <AppShell.Main>
        <ErrorBody
          title="Akes Ditolak"
          description="Anda tidak memiliki izin untuk melihat halaman ini. Silahkan periksa kembali hak akses Anda."
          image={{
            src: '/images/errors/403.svg',
            alt: 'Forbidden Access',
          }}
        >
          <ErrorBody.Action>
            <Button onClick={() => router.back()}>
              Kembali ke Halaman Sebelumnya
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
