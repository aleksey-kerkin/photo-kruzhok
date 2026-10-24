import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { FEED_QUERY_KEY } from "./cache.js";
import { useLikePost } from "./useLikePost.js";

describe("useLikePost hook", () => {
  it("returns the API payload on success", async () => {
    const cache = new QueryClient();
    cache.setQueryData(FEED_QUERY_KEY, {
      pages: [{ results: [{ id: 3, likes_count: 0, liked_by_me: false }], next_cursor: null, has_next: false }],
      pageParams: [undefined],
    });

    vi.stubGlobal(
      "fetch",
      vi.fn(async () => ({
        ok: true,
        status: 200,
        json: async () => ({ liked_by_me: true, likes_count: 1 }),
      })),
    );

    const { result } = renderHook(() => useLikePost(), {
      wrapper: ({ children }) => (
        <QueryClientProvider client={cache}>{children}</QueryClientProvider>
      ),
    });

    await result.current.mutateAsync({ postId: 3, liked: true });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    vi.unstubAllGlobals();
  });
});
