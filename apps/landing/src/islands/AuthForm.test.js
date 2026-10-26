import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

test("the auth island has the Russian fields", () => {
  const source = readFileSync(new URL("./AuthForm.vue", import.meta.url), "utf8");
  assert.match(source, /Имя/);
  assert.match(source, /Пароль/);
  assert.match(source, /Почта/);
  assert.match(source, /from "\.\/session\.js"/);
});
