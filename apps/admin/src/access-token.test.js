import { describe, expect, it } from "vitest";

import { useAccessToken } from "./composables/useAccessToken.js";

describe("useAccessToken", () => {
  it("stores and clears the access token", () => {
    const { accessToken, setAccessToken, clearAccessToken } = useAccessToken();

    setAccessToken("leader-token");
    expect(accessToken.value).toBe("leader-token");

    clearAccessToken();
    expect(accessToken.value).toBeNull();
  });
});
