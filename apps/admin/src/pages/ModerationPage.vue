<template>
  <section>
    <h1>Модерация</h1>

    <p v-if="hiddenPostsQuery.isPending.value">Загрузка…</p>
    <p v-else-if="forbidden">Недостаточно прав</p>
    <p v-else-if="hiddenPostsQuery.isError.value">Не удалось загрузить список</p>

    <ul v-else-if="posts.length">
      <li v-for="post in posts" :key="post.id">
        <span>{{ post.caption || `Пост ${post.id}` }}</span>
        <button
          type="button"
          :disabled="restoreMutation.isPending.value"
          @click="restoreMutation.mutate(post.id)"
        >
          Восстановить
        </button>
      </li>
    </ul>
    <p v-else>Скрытых постов нет</p>
  </section>
</template>

<script setup>
import { useMutation, useQuery, useQueryClient } from "@tanstack/vue-query";
import { computed } from "vue";

import { isPermissionDenied } from "../api/errors.js";
import { useApiClient } from "../composables/useApiClient.js";

const HIDDEN_POSTS_QUERY_KEY = ["posts", "hidden"];

const client = useApiClient();
const queryClient = useQueryClient();

const hiddenPostsQuery = useQuery({
  queryKey: HIDDEN_POSTS_QUERY_KEY,
  queryFn: () => client.request("/api/posts?status=hidden"),
});

const forbidden = computed(() => isPermissionDenied(hiddenPostsQuery.data.value));

const posts = computed(() => {
  const data = hiddenPostsQuery.data.value;
  if (!data || isPermissionDenied(data)) {
    return [];
  }
  return data.results ?? [];
});

const restoreMutation = useMutation({
  mutationFn: (postId) =>
    client.request(`/api/posts/${postId}/restore`, {
      method: "POST",
    }),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: HIDDEN_POSTS_QUERY_KEY });
  },
});
</script>
