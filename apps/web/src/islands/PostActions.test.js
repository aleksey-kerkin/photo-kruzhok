import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

test("guests are sent to login", () => {
  const source = readFileSync(new URL("./PostActions.vue", import.meta.url), "utf8");
  assert.match(source, /href="\/login"/);
  assert.match(source, /restoreAccessToken/);
});
