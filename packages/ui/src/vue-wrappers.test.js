import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

test("Button.vue exposes pk-button class", () => {
  const src = readFileSync(new URL("./Button.vue", import.meta.url), "utf8");
  assert.match(src, /pk-button/);
});
