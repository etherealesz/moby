import { Group, Pagination } from '@mantine/core';

export default function PaginationBottom() {
  return (
    <Pagination.Root total={0}>
      <Group gap={5} justify="center">
        <Pagination.First />
        <Pagination.Previous />
        <Pagination.Next />
        <Pagination.Last />
      </Group>
    </Pagination.Root>
  );
}
