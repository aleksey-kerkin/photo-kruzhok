import assert from "node:assert/strict";
import test from "node:test";

test("restoreAccessToken calls refresh once", async () => {
  let calls = 0;
  globalThis.fetch = async () => {
    calls += 1;
    return { ok: true, json: async () => ({ access: "token-1" }) };
  };
  const { restoreAccessToken, getAccessToken, resetAccessToken } = await import("./session.js");
  resetAccessToken();
  assert.equal(await restoreAccessToken(), "token-1");
  assert.equal(await restoreAccessToken(), "token-1");
  assert.equal(calls, 1);
  assert.equal(getAccessToken(), "token-1");
});
