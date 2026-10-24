import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

import { vitestCoverage } from "../../vitest.coverage.shared.mjs";

const apiProxy = {
  "/api": "http://127.0.0.1:8000",
};

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: apiProxy,
  },
  preview: {
    port: 5173,
    proxy: apiProxy,
  },
  test: {
    environment: "jsdom",
    coverage: {
      ...vitestCoverage,
      include: ["src/**/*.{js,jsx}"],
      exclude: [...vitestCoverage.exclude, "src/main.jsx"],
    },
  },
});
