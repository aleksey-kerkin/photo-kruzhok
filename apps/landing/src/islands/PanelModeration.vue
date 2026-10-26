<script setup>
import { ref } from "vue";
import { getAccessToken, restoreAccessToken } from "./session.js";

function isPermissionDenied(body) {
  return (
    body != null &&
    typeof body === "object" &&
    "code" in body &&
    body.code === "permission_denied"
  );
}

const sessionLoading = ref(true);
const isAuthenticated = ref(false);
const postsLoading = ref(false);
const forbidden = ref(false);
const loadError = ref(false);
const posts = ref([]);
const restorePending = ref(false);

async function loadHiddenPosts() {
  postsLoading.value = true;
  forbidden.value = false;
  const response = await fetch("/api/posts?status=hidden", {
    headers: { Authorization: `Bearer ${getAccessToken()}` },
  });
  const body = await response.json();
  postsLoading.value = false;
  if (isPermissionDenied(body)) {
    forbidden.value = true;
    return;
  }
  if (!response.ok) {
    loadError.value = true;
    return;
  }
  posts.value = body.results ?? [];
}

restoreAccessToken().then(async (token) => {
  isAuthenticated.value = token != null;
  sessionLoading.value = false;
  if (!token) {
    return;
  }
  await loadHiddenPosts();
});

async function restorePost(postId) {
  restorePending.value = true;
  await fetch(`/api/posts/${postId}/restore`, {
    method: "POST",
    headers: { Authorization: `Bearer ${getAccessToken()}` },
  });
  restorePending.value = false;
  await loadHiddenPosts();
}
</script>

<template>
  <section>
    <h1>Модерация</h1>

    <p v-if="sessionLoading">Загрузка…</p>
    <p v-else-if="!isAuthenticated">
      <a href="/login">Войти</a>
    </p>

    <template v-else>
      <p v-if="postsLoading">Загрузка…</p>
      <p v-else-if="forbidden">Недостаточно прав</p>
      <p v-else-if="loadError">Не удалось загрузить список</p>

      <ul v-else-if="posts.length">
        <li v-for="post in posts" :key="post.id">
          <span>{{ post.caption || `Пост ${post.id}` }}</span>
          <button type="button" :disabled="restorePending" @click="restorePost(post.id)">
            Восстановить
          </button>
        </li>
      </ul>
      <p v-else>Скрытых постов нет</p>
    </template>
  </section>
</template>
