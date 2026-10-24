import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

test("tokens.scss defines color custom properties without @import", () => {
  const source = readFileSync(new URL("./tokens.scss", import.meta.url), "utf8");
  assert.match(source, /oklch\(from var\(--pk-color-accent\)/);
  assert.doesNotMatch(source, /@import/);
});
