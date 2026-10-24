export const FEED_QUERY_KEY = ["posts", "feed"];

function patchPostLike(post, liked) {
  if (post.id === undefined) {
    return post;
  }

  const wasLiked = Boolean(post.liked_by_me);
  if (wasLiked === liked) {
    return post;
  }

  const likes_count = Math.max(
    0,
    post.likes_count + (liked ? 1 : -1),
  );

  return { ...post, liked_by_me: liked, likes_count };
}

function patchFeedPage(page, postId, liked) {
  if (!page?.results) {
    return page;
  }

  return {
    ...page,
    results: page.results.map((post) =>
      post.id === postId ? patchPostLike(post, liked) : post,
    ),
  };
}

export function setLiked(cache, postId, liked) {
  const previous = cache.getQueryData(FEED_QUERY_KEY);

  cache.setQueryData(FEED_QUERY_KEY, (current) => {
    if (!current?.pages) {
      return current;
    }

    return {
      ...current,
      pages: current.pages.map((page) => patchFeedPage(page, postId, liked)),
    };
  });

  return previous;
}
