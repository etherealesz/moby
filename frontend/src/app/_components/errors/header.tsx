'use client';

import { useEffect, useState } from 'react';
import { Anchor, Container, Text, Title } from '@mantine/core';
import { formatDisplayDateTimeWithSeparator } from '@/src/shared/utils/datetime';

interface IErrorHeaderProps {
  errorCode: number;
  errorDescription: string;
  requestId?: string;
}

export function ErrorHeader({
  errorCode,
  errorDescription,
  requestId,
}: IErrorHeaderProps) {
  const currentDate = new Date();
  const [loginUrl, setLoginUrl] = useState<string | null>(null);

  useEffect(() => {
    setLoginUrl(
      `${window.location.protocol}//${window.location.hostname}/login`
    );
  }, []);

  return (
    <Container maw="100%" bg="brand.5" c="white" p="xs" m={0}>
      <Container maw="38rem" mx="auto" ta="center">
        <Text fz="xs">
          {currentDate &&
            formatDisplayDateTimeWithSeparator(currentDate, {
              separator: '; ',
            })}
          {loginUrl && (
            <>
              {' | '}
              <Anchor href="/login" fz="xs" c="white">
                {loginUrl}
              </Anchor>
            </>
          )}
          {requestId && ` | ID: ${requestId}`}
        </Text>
        <Title order={5}>
          Error {errorCode} - {errorDescription}
        </Title>
      </Container>
    </Container>
  );
}
