import {
  IconChevronRight,
  IconInfoCircle,
  IconStar,
} from '@tabler/icons-react';
import {
  Badge,
  Button,
  Group,
  Image,
  Progress,
  Text,
  TextInput,
} from '@mantine/core';

interface IDefaultCardFieldProps {
  text: string;
}

interface IDefaultCardFieldWrapperProps {
  children: React.ReactNode;
}

interface IDefaultCardBottomActionProps {
  content: any;
}

interface IDefaultCardImageProps {
  src: string;
  fallbackImageDimensions: {
    width: number;
    height: number;
  };
}

export function DefaultCardLabel({ text }: IDefaultCardFieldProps) {
  return (
    <Badge color="blue" variant="light" size="xs">
      {text}
    </Badge>
  );
}

export function DefaultCardStatus({ text }: IDefaultCardFieldProps) {
  return (
    <Badge color="green" variant="filled" size="xs">
      {text}
    </Badge>
  );
}

export function DefaultCardTitle({ text }: IDefaultCardFieldProps) {
  return (
    <Text
      fw={700}
      size="sm"
      className="leading-tight wrap-break-word text-blue-600 uppercase"
    >
      {text}
    </Text>
  );
}

export function DefaultCardSubtitle({ text }: IDefaultCardFieldProps) {
  return (
    <Text size="xs" c="dimmed" className="mt-0.5 wrap-break-word">
      {text}
    </Text>
  );
}

export function DefaultCardTitleRightButton({ text }: IDefaultCardFieldProps) {
  return (
    <Button variant="subtle" size="compact-xs" className="h-auto px-1">
      {text}
    </Button>
  );
}

export function DefaultCardSubtitleRightButton(props: IDefaultCardFieldProps) {
  return (
    <Text
      size="xs"
      c="dimmed"
      className="cursor-pointer text-right hover:underline"
      style={{ fontSize: '10px' }}
    >
      {props.text}
    </Text>
  );
}

export function DefaultCardTag({ text }: IDefaultCardFieldProps) {
  return (
    <Badge variant="outline" size="xs" className="h-5 max-w-full">
      <span className="block truncate" style={{ fontSize: '10px' }}>
        {text}
      </span>
    </Badge>
  );
}

export function DefaultCardTagWrapper({
  children,
}: IDefaultCardFieldWrapperProps) {
  return (
    <Group gap={4} className="mt-0.5 flex-wrap">
      {children}
    </Group>
  );
}

export function DefaultCardRating({ text }: IDefaultCardFieldProps) {
  return (
    <Group gap={2} align="center">
      <IconStar size={12} className="fill-yellow-400 text-yellow-400" />
      <Text size="xs" fw={500}>
        {text}
      </Text>
    </Group>
  );
}

export function DefaultCardLowerBody({ text }: IDefaultCardFieldProps) {
  return (
    <Text size="xs" className="wrap-break-word">
      {text}
    </Text>
  );
}

export function DefaultCardBody({ text }: IDefaultCardFieldProps) {
  return (
    <Text size="xs" className="mt-1 line-clamp-2 wrap-break-word">
      {text}
    </Text>
  );
}

export function DefaultCardProgressBar({ text }: IDefaultCardFieldProps) {
  return (
    <div className="mt-1 w-full">
      <Progress value={Number(text)} size="xs" radius="xl" />
    </div>
  );
}

export function DefaultCardInformationText({ text }: IDefaultCardFieldProps) {
  return (
    <Group gap={4}>
      <IconInfoCircle size={14} className="text-gray-500" />
      <Text size="xs" c="dimmed">
        {text}
      </Text>
    </Group>
  );
}

export function DefaultCardPriceTag({ text }: IDefaultCardFieldProps) {
  return (
    <Text fw={700} size="sm" c="brand.5">
      {text}
    </Text>
  );
}

export function DefaultCardExtraStatus({ text }: IDefaultCardFieldProps) {
  return (
    <Text c="dimmed" className="italic" style={{ fontSize: '10px' }}>
      {text}
    </Text>
  );
}

export function DefaultCardInputField({
  text: placeholder,
}: IDefaultCardFieldProps) {
  return (
    <TextInput
      placeholder={String(placeholder)}
      size="xs"
      className="mt-1"
      styles={{
        input: { height: '24px', minHeight: '24px', fontSize: '12px' },
      }}
    />
  );
}

export function DefaultCardBottomActionButton({
  content,
}: IDefaultCardBottomActionProps) {
  if (typeof content !== 'string') {
    return content;
  }

  return (
    <Button variant="light" size="compact-xs" fullWidth className="sm:w-auto">
      {content}
    </Button>
  );
}

export function DefaultCardBottomLeftActionButton({
  content,
}: IDefaultCardBottomActionProps) {
  if (typeof content !== 'string') {
    return content;
  }

  return (
    <Button variant="outline" size="compact-xs" className="flex-1 sm:flex-none">
      {content}
    </Button>
  );
}

export function DefaultCardBottomRightActionButton({
  content,
}: IDefaultCardBottomActionProps) {
  if (typeof content !== 'string') {
    return content;
  }

  return (
    <Button variant="filled" size="compact-xs" className="flex-1 sm:flex-none">
      {content}
    </Button>
  );
}

export function DefaultCardImage({
  src,
  fallbackImageDimensions,
}: IDefaultCardImageProps) {
  const fallbackImageDimensionString = `${fallbackImageDimensions?.height}x${fallbackImageDimensions?.width}`;
  const fallbackImageSrc = `https://placehold.co/${fallbackImageDimensionString}?text=No Image`;

  return (
    <Image
      src={src}
      fit="cover"
      w="100%"
      h="100%"
      fallbackSrc={fallbackImageSrc}
      alt={src}
    />
  );
}

export function DefaultCardExtraButton({ text }: IDefaultCardFieldProps) {
  return (
    <Button
      variant="default"
      size="compact-xs"
      className="flex h-full min-h-20 w-20 flex-col gap-1"
    >
      <IconChevronRight size={20} />
      <span className="text-center text-[10px] leading-tight whitespace-normal">
        {text}
      </span>
    </Button>
  );
}
