import assert from "node:assert/strict";
import test from "node:test";

import { createClient } from "./src/client.js";

test("retries once after 401 and returns the second response body", async () => {
  let fetchCalls = 0;
  let refreshCalls = 0;

  const fetchImpl = async () => {
    fetchCalls += 1;
    if (fetchCalls === 1) {
      return {
        ok: false,
        status: 401,
        json: async () => ({}),
      };
    }
    return {
      ok: true,
      status: 200,
      json: async () => ({ data: "ok" }),
    };
  };

  const refresh = async () => {
    refreshCalls += 1;
  };

  const client = createClient({
    fetchImpl,
    getAccessToken: () => "access-token",
    refresh,
  });

  const body = await client.request("/api/example");

  assert.equal(refreshCalls, 1);
  assert.equal(fetchCalls, 2);
  assert.deepEqual(body, { data: "ok" });
});

test("returns API error body on second 401 without throwing", async () => {
  const errorBody = {
    code: "not_authenticated",
    message: "Invalid token",
    fields: { detail: "Token expired" },
  };

  const fetchImpl = async () => ({
    ok: false,
    status: 401,
    json: async () => errorBody,
  });

  let refreshCalls = 0;
  const refresh = async () => {
    refreshCalls += 1;
  };

  const client = createClient({
    fetchImpl,
    getAccessToken: () => "access-token",
    refresh,
  });

  const body = await client.request("/api/example");

  assert.equal(refreshCalls, 1);
  assert.deepEqual(body, errorBody);
});
