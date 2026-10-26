import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

test("the photo grid is CSS and the column is 72ch", () => {
  const source = readFileSync(new URL("./grid.scss", import.meta.url), "utf8");
  assert.match(source, /\.pk-grid\s*\{[^}]*display:\s*grid/s);
  assert.match(source, /\.pk-column\s*\{[^}]*max-width:\s*72ch/s);
  assert.doesNotMatch(source, /masonry/);
});
