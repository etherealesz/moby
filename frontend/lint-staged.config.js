/**
 * @filename: lint-staged.config.js
 * @type {import('lint-staged').Configuration}
 */
export default {
  '**/*.{ts,tsx,js,jsx,mjs,cjs,css,md}': (filenames) => [
    // `eslint --fix ${filenames.map((filename) => `"${filename}"`).join(' ')}`,
    // `stylelint --fix ${filenames
    //   .filter((filename) => filename.endsWith('.css'))
    //   .map((filename) => `"${filename}"`)
    //   .join(' ')}`,
    `prettier --write ${filenames.map((filename) => `"${filename}"`).join(' ')}`,
  ],
};
