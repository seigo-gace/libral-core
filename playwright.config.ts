import { defineConfig, devices } from "@playwright/test";

const PORT = parseInt(process.env.PORT ?? "5000", 10);
const baseURL = process.env.PLAYWRIGHT_BASE_URL ?? `http://127.0.0.1:${PORT}`;

/**
 * 稼働テスト: 事前に npm run dev または npm run start でサーバーを起動してから
 * npx playwright test を実行する。
 */
export default defineConfig({
  testDir: "e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: 1,
  reporter: "list",
  use: {
    baseURL,
    trace: "on-first-retry",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  timeout: 15000,
  expect: { timeout: 5000 },
});
