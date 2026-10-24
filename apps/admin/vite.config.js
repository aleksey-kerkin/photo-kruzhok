import vue from "@vitejs/plugin-vue";
import { defineConfig } from "vite";

import { vitestCoverage } from "../../vitest.coverage.shared.mjs";

const apiProxy = {
  "/api": "http://127.0.0.1:8000",
};

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5174,
    proxy: apiProxy,
  },
  preview: {
    port: 5174,
    proxy: apiProxy,
  },
  test: {
    environment: "jsdom",
    include: ["src/**/*.test.js"],
    coverage: {
      ...vitestCoverage,
      include: ["src/**/*.{js,vue}"],
      exclude: [...vitestCoverage.exclude, "src/main.js"],
    },
  },
});
