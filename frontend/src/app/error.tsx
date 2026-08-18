'use client';

import { HttpStatusCode } from 'axios';
import { AppShell, Button } from '@mantine/core';
import { ErrorBody } from './_components/errors/body';
import { ErrorFooter } from './_components/errors/footer';
import { ErrorHeader } from './_components/errors/header';

interface IErrorProps {
  error: Error & { digest?: string };
  reset: () => void;
}

export default function Error({ error: error, reset }: IErrorProps) {
  return (
    <AppShell>
      <AppShell.Header>
        <ErrorHeader
          errorCode={HttpStatusCode.InternalServerError}
          errorDescription="Kesalahan Internal Server"
        />
      </AppShell.Header>

      <AppShell.Main>
        <ErrorBody
          title="Kesalahan Server Internal"
          description="Terjadi masalah yang tidak terduga pada server kami. Tim teknis sedang berupaya memperbaikinya. Silahkan coba kembali dalam beberapa menit."
          image={{
            src: '/images/errors/500.svg',
            alt: 'Internal Server Error',
          }}
        >
          <ErrorBody.Action>
            <Button onClick={() => reset()}>Muat Ulang</Button>
          </ErrorBody.Action>
        </ErrorBody>
      </AppShell.Main>

      <AppShell.Footer>
        <ErrorFooter />
      </AppShell.Footer>
    </AppShell>
  );
}
