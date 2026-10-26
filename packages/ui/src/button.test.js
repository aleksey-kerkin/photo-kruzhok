import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

test("the button block nests its modifier", () => {
  const source = readFileSync(new URL("./button.scss", import.meta.url), "utf8");
  assert.match(source, /\.pk-button\s*\{/);
  assert.match(source, /&--primary/);
});
