import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

test("openPhoto loads Fancybox only when called", () => {
  const source = readFileSync(new URL("./openPhoto.js", import.meta.url), "utf8");
  assert.match(source, /import\("@fancyapps\/ui\/dist\/fancybox\/index\.js"\)/);
  assert.doesNotMatch(source, /^import .*@fancyapps\/ui/m);
});
