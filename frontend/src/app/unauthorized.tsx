'use client';

import { useRouter } from 'next/navigation';
import { HttpStatusCode } from 'axios';
import { Anchor, AppShell, Button, Stack, Text } from '@mantine/core';
import { ErrorBody } from './_components/errors/body';
import { ErrorFooter } from './_components/errors/footer';
import { ErrorHeader } from './_components/errors/header';

export default function UnauthorizedPage() {
  const router = useRouter();

  return (
    <AppShell>
      <AppShell.Header>
        <ErrorHeader
          errorCode={HttpStatusCode.Unauthorized}
          errorDescription="Akses Dibatasi"
        />
      </AppShell.Header>

      <AppShell.Main>
        <ErrorBody
          image={{
            src: '/images/errors/401.svg',
            alt: 'Unauthorized Access',
          }}
          title="Akses Halaman Dibatasi"
          description="Halaman ini memerlukan otentikasi. Anda harus login untuk bisa mengaksesnya."
        >
          <ErrorBody.Action>
            <Stack align="center">
              <Button onClick={() => router.replace('/login')}>Masuk</Button>
              <Text size="sm">
                Belum punya akun?{' '}
                <Anchor href="/register" fw="bold">
                  Daftar Sekarang!
                </Anchor>
              </Text>
            </Stack>
          </ErrorBody.Action>
        </ErrorBody>
      </AppShell.Main>

      <AppShell.Footer>
        <ErrorFooter />
      </AppShell.Footer>
    </AppShell>
  );
}
