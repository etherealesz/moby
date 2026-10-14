'use client';

import Link from 'next/link';
import clsx from 'clsx';
import { Burger, Drawer } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { NAV_ITEMS, type NavHref } from './nav-items';
import classes from './layout.module.css';

export function MobileMenu({ active }: { active: NavHref }) {
  const [opened, { toggle, close }] = useDisclosure(false);

  return (
    <>
      <Burger
        opened={opened}
        onClick={toggle}
        size="md"
        aria-label={opened ? 'Tutup menu' : 'Buka menu'}
      />
      <Drawer
        opened={opened}
        onClose={close}
        position="right"
        size="80%"
        title="Menu"
      >
        <nav className={classes.drawerNav} aria-label="Navigasi utama">
          {NAV_ITEMS.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              onClick={close}
              aria-current={item.href === active ? 'page' : undefined}
              className={clsx(
                classes.drawerLink,
                item.href === active && classes.drawerLinkActive
              )}
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </Drawer>
    </>
  );
}
