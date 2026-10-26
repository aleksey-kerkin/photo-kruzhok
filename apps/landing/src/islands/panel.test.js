import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

test("panel islands render the forbidden sentence", () => {
  for (const name of ["PanelChallenge.vue", "PanelModeration.vue", "PanelStats.vue"]) {
    const source = readFileSync(new URL(`./${name}`, import.meta.url), "utf8");
    assert.match(source, /Недостаточно прав/);
    assert.doesNotMatch(source, /vue-router/);
  }
});
