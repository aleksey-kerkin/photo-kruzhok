<script setup>
import { onMounted, ref } from "vue";
import { api, isApiError } from "./api.js";
import { restoreAccessToken } from "./session.js";

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
const challengeLoading = ref(false);
const challengeForbidden = ref(false);
const challengeError = ref(false);
const challenge = ref(null);

const submissionsLoading = ref(false);
const submissionsForbidden = ref(false);
const submissions = ref([]);
const votePending = ref(false);

async function loadSubmissions(challengeId) {
  submissionsLoading.value = true;
  submissionsForbidden.value = false;
  const body = await api.request(`/api/challenges/${challengeId}/submissions`);
  submissionsLoading.value = false;
  if (isPermissionDenied(body)) {
    submissionsForbidden.value = true;
    return;
  }
  submissions.value = body.results ?? [];
}

onMounted(() => {
  restoreAccessToken().then(async (token) => {
    isAuthenticated.value = token != null;
    sessionLoading.value = false;
    if (!token) {
      return;
    }
    challengeLoading.value = true;
    const body = await api.request("/api/challenges/current");
    challengeLoading.value = false;
    if (isPermissionDenied(body)) {
      challengeForbidden.value = true;
      return;
    }
    if (isApiError(body)) {
      challengeError.value = true;
      return;
    }
    challenge.value = body;
    await loadSubmissions(body.id);
  });
});

function submissionCaption(submission) {
  const caption = submission.post?.caption;
  if (caption) {
    return caption;
  }
  return `Заявка ${submission.id}`;
}

async function vote(submissionId) {
  if (!challenge.value) {
    return;
  }
  votePending.value = true;
  await api.request(`/api/challenges/${challenge.value.id}/votes`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ submission_id: submissionId }),
  });
  votePending.value = false;
  await loadSubmissions(challenge.value.id);
}
</script>

<template>
  <section>
    <h1>Тема</h1>

    <p v-if="sessionLoading">Загрузка…</p>
    <p v-else-if="!isAuthenticated">
      <a href="/login">Войти</a>
    </p>

    <template v-else>
      <p v-if="challengeLoading">Загрузка…</p>
      <p v-else-if="challengeForbidden">Недостаточно прав</p>
      <p v-else-if="challengeError">Не удалось загрузить тему</p>

      <template v-else-if="challenge">
        <h2>{{ challenge.title }}</h2>
        <p v-if="challenge.description">{{ challenge.description }}</p>
        <p>
          <span>Статус: {{ challenge.status }}</span>
        </p>

        <h3>Заявки</h3>
        <p v-if="submissionsLoading">Загрузка заявок…</p>
        <p v-else-if="submissionsForbidden">Недостаточно прав</p>
        <ul v-else-if="submissions.length">
          <li v-for="submission in submissions" :key="submission.id">
            <span>{{ submissionCaption(submission) }}</span>
            <button type="button" :disabled="votePending" @click="vote(submission.id)">
              Проголосовать
            </button>
          </li>
        </ul>
        <p v-else>Заявок пока нет</p>
      </template>
    </template>
  </section>
</template>
