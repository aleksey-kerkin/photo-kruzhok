import { QueryClient } from "@tanstack/react-query";
import { describe, expect, it } from "vitest";

import { FEED_QUERY_KEY, setLiked } from "./cache.js";

describe("setLiked edge cases", () => {
  it("returns the previous cache when pages are missing", () => {
    const cache = new QueryClient();
    const previous = setLiked(cache, 1, true);
    expect(previous).toBeUndefined();
  });

  it("ignores feed pages without results", () => {
    const cache = new QueryClient();
    cache.setQueryData(FEED_QUERY_KEY, {
      pages: [{}],
      pageParams: [undefined],
    });

    setLiked(cache, 1, true);
    const data = cache.getQueryData(FEED_QUERY_KEY);
    expect(data.pages[0].results).toBeUndefined();
  });

  it("does not change a post that is already in the target like state", () => {
    const cache = new QueryClient();
    cache.setQueryData(FEED_QUERY_KEY, {
      pages: [{ results: [{ id: 3, likes_count: 2, liked_by_me: true }] }],
      pageParams: [undefined],
    });

    setLiked(cache, 3, true);
    const data = cache.getQueryData(FEED_QUERY_KEY);
    expect(data.pages[0].results[0].likes_count).toBe(2);
  });

  it("leaves posts without ids unchanged", () => {
    const cache = new QueryClient();
    cache.setQueryData(FEED_QUERY_KEY, {
      pages: [{ results: [{ likes_count: 0, liked_by_me: false }] }],
      pageParams: [undefined],
    });

    setLiked(cache, 1, true);
    const data = cache.getQueryData(FEED_QUERY_KEY);
    expect(data.pages[0].results[0].liked_by_me).toBe(false);
  });
});
