'use client';

import { useRouter } from 'next/navigation';
import { Button, Container, Group, Stack, Text, Title } from '@mantine/core';

export function ErrorFooter() {
  const router = useRouter();

  return (
    <Container
      m={0}
      maw="100%"
      bg="brand.5"
      c="white"
      pt="xs"
      px="xs"
      pb={{
        base: 'lg',
        sm: 'xs',
      }}
    >
      <Group
        justify="space-between"
        mx="auto"
        w={{
          base: 'calc(100% - 2rem)',
          sm: '36rem',
          md: '44rem',
        }}
      >
        <Stack gap={0}>
          <Title
            order={5}
            display={{
              base: 'none',
              sm: 'block',
            }}
          >
            Anda masih mengalami masalah yang sama?
          </Title>
          <Text
            fz={{
              base: 'sm',
              sm: 'xs',
            }}
          >
            Silahkan hubungi team kami atau hubungi kami melalui tombol berikut
          </Text>
        </Stack>

        <Group
          justify="flex-end"
          w={{
            base: '100%',
            sm: 'auto',
          }}
        >
          <Button
            variant="outline"
            onClick={() => router.replace('/contact-us')}
            color="white"
          >
            Hubungi Kami
          </Button>
        </Group>
      </Group>
    </Container>
  );
}
