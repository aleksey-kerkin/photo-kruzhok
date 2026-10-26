import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import test from "node:test";

const require = createRequire(import.meta.url);

test("the repo pins Node 22.23.1", () => {
  const root = JSON.parse(
    readFileSync(new URL("../../package.json", import.meta.url), "utf8"),
  );
  assert.equal(root.engines.node, "22.23.1");
  assert.equal(process.version, "v22.23.1");
});

test("installed Astro accepts Node 22.23.1", () => {
  const astro = require("astro/package.json");
  assert.equal(astro.version, "7.4.1");
  assert.equal(astro.engines.node, ">=22.22.0");
});
