'use client';

import { AppShell, Container } from '@mantine/core';

export default function ExampleLayout({
  children,
}: Readonly<React.PropsWithChildren>) {
  return (
    <AppShell>
      <AppShell.Main>
        <Container p="xl">{children}</Container>
      </AppShell.Main>
    </AppShell>
  );
}
