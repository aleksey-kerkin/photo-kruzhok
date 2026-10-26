import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

test("upload and challenge islands send guests to login", () => {
  const upload = readFileSync(new URL("./UploadForm.vue", import.meta.url), "utf8");
  const challenge = readFileSync(new URL("./ChallengeActions.vue", import.meta.url), "utf8");
  assert.match(upload, /Подпись/);
  assert.match(upload, /\/login/);
  assert.match(challenge, /submission_id/);
  assert.match(challenge, /\/login/);
});
