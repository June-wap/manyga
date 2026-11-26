import { defineConfig } from '@playwright/test';
export default defineConfig({
  testDir: '../tests/frontend', workers: 1,
  outputDir: '../runtime/playwright-results',
  use: { baseURL: 'http://127.0.0.1:15173', viewport: { width: 1080, height: 1920 } },
  webServer: [
    { command: 'node node_modules/vite/bin/vite.js --host 127.0.0.1 --port 15173 --strictPort',
      url: 'http://127.0.0.1:15173', reuseExistingServer: false },
    { command: 'node node_modules/vite/bin/vite.js preview --host 127.0.0.1 --port 15174 --strictPort',
      url: 'http://127.0.0.1:15174', reuseExistingServer: false },
  ],
});
