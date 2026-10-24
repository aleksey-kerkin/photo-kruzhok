import { defineConfig } from "@playwright/test";

const LANDING = "http://127.0.0.1:4321";
const WEB = "http://127.0.0.1:5173";
const ADMIN = "http://127.0.0.1:5174";

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
    { name: "landing-home", testMatch: /landing-home\.spec\.js/, use: { baseURL: LANDING } },
    {
      name: "landing-profile",
      testMatch: /landing-profile\.spec\.js/,
      use: { baseURL: LANDING },
    },
    { name: "web-login", testMatch: /web-login\.spec\.js/, use: { baseURL: WEB } },
    {
      name: "web-register",
      testMatch: /web-register\.spec\.js/,
      use: { baseURL: WEB },
    },
    { name: "web-feed", testMatch: /web-feed\.spec\.js/, use: { baseURL: WEB } },
    { name: "web-post", testMatch: /web-post\.spec\.js/, use: { baseURL: WEB } },
    {
      name: "web-profile",
      testMatch: /web-profile\.spec\.js/,
      use: { baseURL: WEB },
    },
    { name: "web-upload", testMatch: /web-upload\.spec\.js/, use: { baseURL: WEB } },
    {
      name: "web-submission",
      testMatch: /web-submission\.spec\.js/,
      use: { baseURL: WEB },
    },
    { name: "web-vote", testMatch: /web-vote\.spec\.js/, use: { baseURL: WEB } },
    {
      name: "admin-challenge",
      testMatch: /admin-challenge\.spec\.js/,
      use: { baseURL: ADMIN },
    },
    {
      name: "admin-moderation",
      testMatch: /admin-moderation\.spec\.js/,
      use: { baseURL: ADMIN },
    },
    { name: "admin-stats", testMatch: /admin-stats\.spec\.js/, use: { baseURL: ADMIN } },
    { name: "auth-env", testMatch: /auth-env\.spec\.js/ },
  ],
  webServer: [
    {
      command: "pnpm --filter @photo-kruzhok/web exec vite preview --host 127.0.0.1 --port 5173",
      url: WEB,
      reuseExistingServer: true,
      timeout: 120_000,
    },
    {
      command: "pnpm --filter @photo-kruzhok/admin exec vite preview --host 127.0.0.1 --port 5174",
      url: ADMIN,
      reuseExistingServer: true,
      timeout: 120_000,
    },
    {
      command:
        "pnpm --filter @photo-kruzhok/landing exec astro preview --host 127.0.0.1 --port 4321",
      url: LANDING,
      reuseExistingServer: true,
      timeout: 120_000,
    },
  ],
});
