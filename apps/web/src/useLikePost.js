import { useMutation, useQueryClient } from "@tanstack/react-query";

import { FEED_QUERY_KEY, setLiked } from "./cache.js";

export function useLikePost() {
  const cache = useQueryClient();

  return useMutation({
    mutationFn: async ({ postId, liked }) => {
      const response = await fetch(`/api/posts/${postId}/like`, {
        method: liked ? "PUT" : "DELETE",
      });
      if (!response.ok) {
        throw new Error("Like request failed");
      }
      return response.json();
    },
    onMutate: ({ postId, liked }) => {
      const previous = setLiked(cache, postId, liked);
      return { previous };
    },
    onError: (_error, _variables, context) => {
      if (context?.previous !== undefined) {
        cache.setQueryData(FEED_QUERY_KEY, context.previous);
      }
    },
  });
}
