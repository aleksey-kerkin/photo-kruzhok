import { describe, expect, it, vi } from "vitest";

import { useApiClient } from "./composables/useApiClient.js";

vi.mock("./composables/useAccessToken.js", () => ({
  useAccessToken: () => ({ accessToken: { value: "token-123" } }),
}));

describe("useApiClient", () => {
  it("forwards the access token to the SDK client", async () => {
    const fetchImpl = vi.fn(async () => ({
      ok: true,
      status: 200,
      json: async () => ({ ok: true }),
    }));
    vi.stubGlobal("fetch", fetchImpl);

    const client = useApiClient();
    await client.request("/api/challenges/current");

    expect(fetchImpl).toHaveBeenCalled();
    const [, init] = fetchImpl.mock.calls[0];
    expect(init.headers.get("Authorization")).toBe("Bearer token-123");
    vi.unstubAllGlobals();
  });
});
