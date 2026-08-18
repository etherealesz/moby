import { Center, Image, Stack, Text, Title } from '@mantine/core';

interface IErrorBodyImageProps {
  src: string;
  alt: string;
}

interface IErrorBodyProps {
  image: IErrorBodyImageProps;
  title: string;
  description: string;
  children?: React.ReactNode;
}

interface IErrorBodyActionProps {
  children: React.ReactNode;
}

export function ErrorBody({
  image,
  title,
  description,
  children,
}: IErrorBodyProps) {
  return (
    <Center h="100dvh" w="100dvw" p="md">
      <Stack
        align="center"
        justify="center"
        c="black"
        gap="0.75rem"
        maw="38rem"
      >
        <Image
          src={image.src}
          alt={image.alt}
          w={{
            base: '16rem',
            xs: '20rem',
            sm: '24rem',
          }}
        />

        <Stack align="center" justify="center" gap="0.125rem">
          <Title order={4}>{title}</Title>
          <Text
            fz={{
              base: 'xs',
              sm: 'sm',
            }}
            ta="center"
          >
            {description}
          </Text>
        </Stack>
        {children}
      </Stack>
    </Center>
  );
}

function ErrorBodyAction({ children }: IErrorBodyActionProps) {
  return children;
}

ErrorBody.Action = ErrorBodyAction;
