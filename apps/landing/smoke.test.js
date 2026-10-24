import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

test("landing shell is present", () => {
  const pkg = JSON.parse(readFileSync(new URL("./package.json", import.meta.url), "utf8"));
  assert.equal(pkg.name, "@photo-kruzhok/landing");
});

test("built home page contains Витрина and anya profile link", () => {
  const html = readFileSync(new URL("./dist/index.html", import.meta.url), "utf8");
  assert.match(html, /Витрина/);
  assert.match(html, /\/profiles\/anya/);
});
