/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // 10-step Mantine brand palette
        brand: {
          0: 'var(--mantine-color-brand-0)',
          1: 'var(--mantine-color-brand-1)',
          2: 'var(--mantine-color-brand-2)',
          3: 'var(--mantine-color-brand-3)',
          4: 'var(--mantine-color-brand-4)',
          5: 'var(--mantine-color-brand-5)',
          6: 'var(--mantine-color-brand-6)',
          7: 'var(--mantine-color-brand-7)',
          8: 'var(--mantine-color-brand-8)',
          9: 'var(--mantine-color-brand-9)',
        },

        // Mantine’s computed primary colors
        'primary-filled': 'var(--mantine-primary-color-filled)',
        'primary-light': 'var(--mantine-primary-color-light)',
        'primary-hover': 'var(--mantine-primary-color-hover)',
      },
    },
  },
  plugins: [],
};
