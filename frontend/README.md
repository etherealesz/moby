# Next.Js Project Template

A modern **Next.js** frontend template with TypeScript, Tailwind CSS, ESLint, Prettier, Jest, and environment-based configuration.
Designed to be scalable, maintainable, and production-ready.

## Tech Stack

- **Next.js** (App Router)
- **TypeScript**
- **Tailwind CSS**
- **ESLint & Prettier**
- **Jest** (unit testing)
- **Husky** (git hooks)
- **Bun / Node.js**
- **PostCSS**
- **Renovate** (dependency updates)

## Build and dev scripts

- `dev` – start dev server
- `build:dev` – bundle application for production in development environment
- `build:staging` – bundle application for production in staging environment
- `build:production` – bundle application for production in production environment
- `analyze` – analyzes application bundle with [@next/bundle-analyzer](https://www.npmjs.com/package/@next/bundle-analyzer)

## Testing scripts

- `typecheck` – checks TypeScript types
- `lint` – runs ESLint
- `prettier:check` – checks files with Prettier
- `jest` – runs jest tests
- `jest:watch` – starts jest watch
- `test` – runs `jest`, `prettier:check`, `lint` and `typecheck` scripts

## Other scripts

- `storybook` – starts storybook dev server
- `storybook:build` – build production storybook bundle to `storybook-static`
- `prettier:write` – formats all files with Prettier
