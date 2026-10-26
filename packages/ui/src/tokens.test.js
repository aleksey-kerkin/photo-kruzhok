import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

test("tokens.scss defines color custom properties without @import", () => {
  const source = readFileSync(new URL("./tokens.scss", import.meta.url), "utf8");
  assert.match(source, /oklch\(from var\(--pk-color-accent\)/);
  assert.doesNotMatch(source, /@import/);
});

test("dark scheme overrides the same token names", () => {
  const source = readFileSync(new URL("./tokens.scss", import.meta.url), "utf8");
  assert.match(source, /@media \(prefers-color-scheme: dark\)/);
  assert.match(source, /--pk-color-bg:\s*oklch\(0\.18 0\.005 78\.3\)/);
  assert.match(source, /--pk-color-surface:\s*oklch\(0\.23 0\.005 78\.3\)/);
  assert.match(source, /--pk-color-text:\s*oklch\(0\.93 0 0\)/);
  assert.match(source, /--pk-color-accent:\s*oklch\(0\.72 0\.12 37\.3\)/);
  assert.doesNotMatch(source, /--pk-color-dark-/);
});
