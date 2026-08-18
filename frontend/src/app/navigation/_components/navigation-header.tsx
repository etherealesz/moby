'use client';

import Image from 'next/image';
import Link from 'next/link';
import { LuHouse } from 'react-icons/lu';
import {
  AppShell,
  Badge,
  Box,
  Burger,
  Button,
  Group,
  Text,
  Title,
} from '@mantine/core';
import { PRIMARY } from '@/lib/constants/colors';

interface INavigationHeaderProps {
  opened: boolean;
  onToggle: () => void;
}

export function NavigationHeader({ opened, onToggle }: INavigationHeaderProps) {
  return (
    <AppShell.Header
      style={{
        backgroundColor: PRIMARY[600],
        borderBottom: '1px solid #014c53',
        boxShadow: '0 2px 10px rgba(2, 98, 107, 0.25)',
      }}
    >
      <Group h="100%" px="md" justify="space-between" align="center">
        <Group gap="sm">
          <Burger
            opened={opened}
            onClick={onToggle}
            hiddenFrom="sm"
            size="sm"
            color="#ffffff"
          />
          <Link
            href="/home"
            style={{
              textDecoration: 'none',
              display: 'flex',
              alignItems: 'center',
              gap: 10,
            }}
          >
            <Image
              src="/images/logo.png"
              alt="TrashNav Logo"
              width={32}
              height={32}
              style={{ borderRadius: 8 }}
            />
            <Box>
              <Title
                order={4}
                style={{ color: '#ffffff', fontWeight: 800, lineHeight: 1.1 }}
              >
                TrashNav
              </Title>
              <Text size="xs" style={{ color: '#b3e3e9', lineHeight: 1 }}>
                Navigasi Rute Pengangkutan
              </Text>
            </Box>
          </Link>
        </Group>

        <Group gap="sm">
          <Button
            component={Link}
            href="/home"
            variant="subtle"
            size="xs"
            leftSection={<LuHouse size={14} />}
            style={{ color: '#ffffff' }}
          >
            Beranda
          </Button>
          <Badge
            size="sm"
            variant="light"
            style={{
              backgroundColor: 'rgba(255, 255, 255, 0.15)',
              color: '#ffffff',
              border: '1px solid rgba(255, 255, 255, 0.25)',
            }}
          >
            Peta Rute Aktif
          </Badge>
        </Group>
      </Group>
    </AppShell.Header>
  );
}
