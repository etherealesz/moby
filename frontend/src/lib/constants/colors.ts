/**
 * TrashNav Design System — Color Tokens
 * Aligned with Mantine `brand` palette (#026D77 / #02626b)
 */

// ── Primary (Brand Teal/Ocean — matches Mantine `brand` in theme.ts) ───────────
export const PRIMARY = {
  50: '#e0f4f6', // Softest light mint/teal
  100: '#b3e3e9', // Light tint
  200: '#80d0da',
  300: '#4dbdcb',
  400: '#1b7c85',
  500: '#026D77', // brand.4 / brand.5 — main brand ocean teal
  600: '#02626b', // brand.5 — header & error pages
  700: '#02575f', // brand.6 / brand.7
  800: '#014c53', // brand.8
  900: '#014147', // brand.9
} as const;

// ── Secondary (Emerald / Eco Accent) ───────────────────────────────────────
export const SECONDARY = {
  50: '#e8f5ee',
  100: '#c5e6d3',
  200: '#9dd4b6',
  300: '#72c298',
  400: '#4cb47f',
  500: '#2a9d8f', // Coral reef / seafoam green
  600: '#21867a',
  700: '#18645b',
  800: '#114a43',
  900: '#0a2e2a',
} as const;

// ── Tertiary (Warm Amber / Orange) ─────────────────────────────────────────
export const TERTIARY = {
  50: '#fff8e1',
  100: '#ffedb3',
  200: '#ffe182',
  300: '#ffd54f',
  400: '#ffca28',
  500: '#e76f51', // Warm Coral / Terra
  600: '#f4a261', // Sandy Orange
  700: '#e65100',
  800: '#bf360c',
  900: '#870000',
} as const;

// ── Semantic ───────────────────────────────────────────────────────────────
export const SEMANTIC = {
  danger: '#e63946', // Crimson Red
  success: '#2a9d8f', // Emerald Teal
  warning: '#e76f51', // Coral Orange
  info: '#026D77', // Brand Teal
} as const;

// ── Surface (Clean light & card backgrounds) ───────────────────────────────
export const SURFACE = {
  base: '#f8fbfc', // clean light page bg
  raised: '#ffffff', // sidebar / cards
  float: '#f0f8f9', // subtle hover / active
  border: '#dbeceb', // soft teal-gray border
  borderStrong: '#a8d5d4',
} as const;

// ── Text colors ────────────────────────────────────────────────────────────
export const TEXT = {
  primary: '#1d2d35', // deep slate
  secondary: '#4a6572', // muted slate
  muted: '#7f9aa6', // subtle secondary
  inverted: '#ffffff',
} as const;

// ── Legacy aliases (backward-compat) ──────────────────────────────────────
export const COLORS = {
  deepForest: PRIMARY[800],
  seaGreen: PRIMARY[500],
  goldenGlow: TERTIARY[600],
  tigerOrange: TERTIARY[500],
  pureRed: SEMANTIC.danger,
} as const;
