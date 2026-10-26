import { defineConfig } from "@playwright/test";

const BASE = "http://127.0.0.1:4321";

export default defineConfig({
  testDir: "./e2e",
  timeout: 60_000,
  expect: { timeout: 15_000 },
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 1 : 0,
  reporter: [["list"]],
  use: {
    trace: "on-first-retry",
  },
  projects: [
    { name: "landing-home", testMatch: /landing-home\.spec\.js/, use: { baseURL: BASE } },
    {
      name: "landing-profile",
      testMatch: /landing-profile\.spec\.js/,
      use: { baseURL: BASE },
    },
    { name: "web-login", testMatch: /web-login\.spec\.js/, use: { baseURL: BASE } },
    { name: "web-post", testMatch: /web-post\.spec\.js/, use: { baseURL: BASE } },
    {
      name: "admin-challenge",
      testMatch: /admin-challenge\.spec\.js/,
      use: { baseURL: BASE },
    },
    { name: "auth-env", testMatch: /auth-env\.spec\.js/ },
  ],
  webServer: {
    command: "pnpm --filter @photo-kruzhok/web preview --host 127.0.0.1 --port 4321",
    url: BASE,
    reuseExistingServer: true,
    timeout: 120_000,
  },
});
