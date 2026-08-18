'use client';

import { useMemo } from 'react';
import { Box, Stack, Text } from '@mantine/core';
import { notifications } from '@mantine/notifications';
import { useRandomColor } from '@/src/modules/example/hooks/use-random-color';

const COLOR_BOX_SIZE = 96;

export default function ExamplePage() {
  const { data: randomColor, error, isLoading } = useRandomColor();

  const hsl = useMemo(() => {
    if (!randomColor) {
      return null;
    }

    return `hsl(${randomColor?.hsl.h}, ${randomColor?.hsl.s}%, ${randomColor?.hsl.l}%)`;
  }, [randomColor?.hsl]);
  const rbg = useMemo(() => {
    if (!randomColor) {
      return null;
    }

    return `rgb(${randomColor?.rgb.r}, ${randomColor?.rgb.g}, ${randomColor?.rgb.b})`;
  }, [randomColor?.rgb]);

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);

      notifications.show({
        message: 'Successfully copied color value to clipboard',
        color: 'green',
      });
    } catch (err) {
      console.error('Failed to copy to clipboard: ', err);
    }
  };

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (error) {
    notifications.show({
      title: 'Error',
      message: 'Failed to load random color',
      color: 'red',
    });

    return <div>Error loading color</div>;
  }

  return (
    <Stack>
      <Text>
        You got <strong>{randomColor?.hex}</strong>
      </Text>
      <Box
        style={{ backgroundColor: randomColor?.hex }}
        w={COLOR_BOX_SIZE}
        h={COLOR_BOX_SIZE}
      />
      <Box
        variant="transparent"
        w="fit-content"
        c="black"
        className="cursor-pointer"
        onClick={() => copyToClipboard(hsl!)}
      >
        HSL: {hsl}
      </Box>
      <Box
        variant="transparent"
        w="fit-content"
        c="black"
        className="cursor-pointer"
        onClick={() => copyToClipboard(rbg!)}
      >
        RGB: {rbg}
      </Box>
    </Stack>
  );
}
