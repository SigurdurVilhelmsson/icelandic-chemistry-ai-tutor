import { defineConfig } from 'vitest/config';

/**
 * Vitest Configuration for API Tests
 *
 * Run tests with:
 *   npm test
 *   npm run test:watch
 *   npm run test:coverage
 */
export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/**',
        '_tests/**',
        '**/*.test.ts',
        '**/*.config.ts',
      ],
    },
    setupFiles: [],
  },
});
