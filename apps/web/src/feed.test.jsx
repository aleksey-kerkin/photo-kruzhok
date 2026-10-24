import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { FEED_QUERY_KEY, setLiked } from "./cache.js";
import HomePage from "./pages/HomePage.jsx";

function makeFeedData(post) {
  return {
    pages: [{ results: [post], next_cursor: null, has_next: false }],
    pageParams: [undefined],
  };
}

describe("feed layout", () => {
  it("wraps posts in shared pk-feed layout classes", () => {
    const post = { id: 1, caption: "Тест", likes_count: 0, liked_by_me: false };
    const cache = new QueryClient();
    cache.setQueryData(FEED_QUERY_KEY, makeFeedData(post));

    const { container } = render(
      <QueryClientProvider client={cache}>
        <HomePage />
      </QueryClientProvider>,
    );

    expect(container.querySelector(".pk-feed")).not.toBeNull();
    expect(container.querySelector(".pk-feed__card")).not.toBeNull();
  });
});

describe("setLiked", () => {
  it("flips a post from unliked to liked and restores the previous snapshot", () => {
    const post = { id: 42, likes_count: 0, liked_by_me: false };
    const cache = new QueryClient();
    cache.setQueryData(FEED_QUERY_KEY, makeFeedData(post));

    const previous = setLiked(cache, 42, true);

    const afterLike = cache.getQueryData(FEED_QUERY_KEY);
    expect(afterLike.pages[0].results[0].liked_by_me).toBe(true);
    expect(afterLike.pages[0].results[0].likes_count).toBe(1);

    cache.setQueryData(FEED_QUERY_KEY, previous);

    const restored = cache.getQueryData(FEED_QUERY_KEY);
    expect(restored.pages[0].results[0].liked_by_me).toBe(false);
    expect(restored.pages[0].results[0].likes_count).toBe(0);
  });
});
