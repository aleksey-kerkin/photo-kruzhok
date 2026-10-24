/** Shared Vitest coverage settings for handwritten JS/JSX. */
export const vitestCoverage = {
  provider: "v8",
  reporter: ["text", "text-summary"],
  thresholds: {
    lines: 90,
  },
  exclude: [
    "coverage/**",
    "dist/**",
    "**/node_modules/**",
    "**/*.test.{js,jsx}",
    "**/smoke.test.js",
    "**/migrations/**",
    "**/schema.d.ts",
    "**/*.config.{js,mjs,cjs}",
    "**/.storybook/**",
  ],
};
