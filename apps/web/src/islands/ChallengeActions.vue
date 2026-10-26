<script setup>
import { onMounted, ref } from "vue";
import { api, isApiError } from "./api.js";
import { restoreAccessToken } from "./session.js";

const sessionLoading = ref(true);
const isAuthenticated = ref(false);
const challenge = ref(null);
const postId = ref("");
const submissionId = ref("");
const errorMessage = ref("");

onMounted(() => {
  restoreAccessToken().then(async (token) => {
    isAuthenticated.value = token != null;
    sessionLoading.value = false;
    if (!token) {
      return;
    }
    const body = await api.request("/api/challenges/current");
    if (isApiError(body)) {
      return;
    }
    challenge.value = body;
  });
});

async function onSubmitPost(event) {
  event.preventDefault();
  if (!challenge.value) {
    return;
  }
  errorMessage.value = "";
  const body = await api.request(`/api/challenges/${challenge.value.id}/submissions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ post_id: Number(postId.value) }),
  });
  if (isApiError(body)) {
    errorMessage.value = body.message ?? "";
  }
}

async function onVote(event) {
  event.preventDefault();
  if (!challenge.value) {
    return;
  }
  errorMessage.value = "";
  const body = await api.request(`/api/challenges/${challenge.value.id}/votes`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ submission_id: Number(submissionId.value) }),
  });
  if (isApiError(body)) {
    errorMessage.value = body.message ?? "";
  }
}
</script>

<template>
  <div>
    <p v-if="errorMessage">{{ errorMessage }}</p>
    <p v-if="sessionLoading">Загрузка…</p>
    <template v-else-if="!isAuthenticated">
      <p><a href="/login">Войти, чтобы участвовать в теме недели</a></p>
    </template>
    <template v-else>
      <h2 v-if="challenge">{{ challenge.title }}</h2>
      <form @submit="onSubmitPost">
        <label>
          Номер поста
          <input v-model="postId" name="post_id" type="number" />
        </label>
        <button type="submit">Отправить</button>
      </form>
      <form @submit="onVote">
        <label>
          Номер заявки
          <input v-model="submissionId" name="submission_id" type="number" />
        </label>
        <button type="submit">Голосовать</button>
      </form>
    </template>
  </div>
</template>
