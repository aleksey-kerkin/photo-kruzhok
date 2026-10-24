import { useInfiniteQuery } from "@tanstack/react-query";

import { FEED_QUERY_KEY } from "../cache.js";
import { useLikePost } from "../useLikePost.js";

async function fetchFeedPage({ pageParam }) {
  const params = new URLSearchParams();
  if (pageParam) {
    params.set("cursor", pageParam);
  }
  const query = params.toString();
  const url = query ? `/api/posts?${query}` : "/api/posts";
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error("Feed request failed");
  }
  return response.json();
}

export default function HomePage() {
  const { data, isPending, error } = useInfiniteQuery({
    queryKey: FEED_QUERY_KEY,
    queryFn: fetchFeedPage,
    initialPageParam: undefined,
    getNextPageParam: (lastPage) =>
      lastPage.has_next ? lastPage.next_cursor : undefined,
  });
  const likePost = useLikePost();

  const posts = data?.pages.flatMap((page) => page.results) ?? [];

  return (
    <section>
      <h1>Лента</h1>
      {isPending ? <p>Загрузка…</p> : null}
      {error ? <p>Не удалось загрузить ленту.</p> : null}
      <ul className="pk-feed">
        {posts.map((post) => (
          <li key={post.id} className="pk-feed__card">
            <p>{post.caption ?? post.text ?? `Пост ${post.id}`}</p>
            <button
              type="button"
              aria-pressed={post.liked_by_me}
              onClick={() =>
                likePost.mutate({
                  postId: post.id,
                  liked: !post.liked_by_me,
                })
              }
            >
              {post.liked_by_me ? "Нравится" : "Лайк"} · {post.likes_count}
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}
