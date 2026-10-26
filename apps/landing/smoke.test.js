import assert from "node:assert/strict";
import { readFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";
import test from "node:test";

function walk(dir) {
  return readdirSync(dir).flatMap((name) => {
    const path = join(dir, name);
    return statSync(path).isDirectory() ? walk(path) : [path];
  });
}

test("landing shell is present", () => {
  const pkg = JSON.parse(readFileSync(new URL("./package.json", import.meta.url), "utf8"));
  assert.equal(pkg.name, "@photo-kruzhok/landing");
});

test("built home page contains Витрина and anya profile link", () => {
  const html = readFileSync(new URL("./dist/index.html", import.meta.url), "utf8");
  assert.match(html, /Витрина/);
  assert.match(html, /\/profiles\/anya/);
  assert.match(html, /pk-grid/);
  assert.doesNotMatch(html, /astro-island/);
});

test("the build contains a post route and a profile route", () => {
  const distRoot = new URL("./dist", import.meta.url).pathname;
  const files = walk(distRoot);
  assert.ok(files.some((file) => file.includes("profiles")));

  const serverFiles = walk(join(distRoot, "server"));
  assert.ok(
    serverFiles.some((file) => readFileSync(file, "utf8").includes("Пост не найден")),
    "expected post page in server build",
  );
});
