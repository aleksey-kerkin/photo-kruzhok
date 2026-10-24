import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { FEED_QUERY_KEY } from "./cache.js";
import HomePage from "./pages/HomePage.jsx";

describe("useLikePost", () => {
  it("rolls back the optimistic like when the API fails", async () => {
    const post = { id: 7, caption: "Откат", likes_count: 0, liked_by_me: false };
    const cache = new QueryClient();
    cache.setQueryData(FEED_QUERY_KEY, {
      pages: [{ results: [post], next_cursor: null, has_next: false }],
      pageParams: [undefined],
    });

    vi.stubGlobal(
      "fetch",
      vi.fn(async () => ({
        ok: false,
        status: 500,
        json: async () => ({}),
      })),
    );

    render(
      <QueryClientProvider client={cache}>
        <HomePage />
      </QueryClientProvider>,
    );

    fireEvent.click(screen.getByRole("button", { name: /Лайк/ }));
    await screen.findByRole("button", { name: /Лайк/ });

    const restored = cache.getQueryData(FEED_QUERY_KEY);
    expect(restored.pages[0].results[0].liked_by_me).toBe(false);
    vi.unstubAllGlobals();
  });
});
