import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

import { vitestCoverage } from "../../vitest.coverage.shared.mjs";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    include: ["**/*.test.jsx"],
    coverage: {
      ...vitestCoverage,
      include: ["src/Button.jsx", "src/Field.jsx", "src/Dialog.jsx"],
    },
  },
});
