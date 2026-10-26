<script setup>
import { onMounted, ref } from "vue";
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
const challengeLoading = ref(false);
const currentForbidden = ref(false);
const challengeError = ref(false);
const challenge = ref(null);

const statsLoading = ref(false);
const statsForbidden = ref(false);
const statsError = ref(false);
const stats = ref(null);

async function loadStats(challengeId) {
  statsLoading.value = true;
  statsForbidden.value = false;
  statsError.value = false;
  const response = await fetch(`/api/challenges/${challengeId}/stats`, {
    headers: { Authorization: `Bearer ${getAccessToken()}` },
  });
  const body = await response.json();
  statsLoading.value = false;
  if (isPermissionDenied(body)) {
    statsForbidden.value = true;
    return;
  }
  if (!response.ok) {
    statsError.value = true;
    return;
  }
  stats.value = body;
}

onMounted(() => {
  restoreAccessToken().then(async (token) => {
    isAuthenticated.value = token != null;
    sessionLoading.value = false;
    if (!token) {
      return;
    }
    challengeLoading.value = true;
    const response = await fetch("/api/challenges/current", {
      headers: { Authorization: `Bearer ${getAccessToken()}` },
    });
    const body = await response.json();
    challengeLoading.value = false;
    if (isPermissionDenied(body)) {
      currentForbidden.value = true;
      return;
    }
    if (!response.ok) {
      challengeError.value = true;
      return;
    }
    challenge.value = body;
    await loadStats(body.id);
  });
});
</script>

<template>
  <section>
    <h1>Статистика</h1>

    <p v-if="sessionLoading">Загрузка…</p>
    <p v-else-if="!isAuthenticated">
      <a href="/login">Войти</a>
    </p>

    <template v-else>
      <p v-if="challengeLoading">Загрузка…</p>
      <p v-else-if="currentForbidden">Недостаточно прав</p>
      <p v-else-if="challengeError">Не удалось загрузить тему</p>

      <template v-else-if="challenge">
        <p v-if="statsLoading">Загрузка статистики…</p>
        <p v-else-if="statsForbidden">Недостаточно прав</p>
        <p v-else-if="statsError">Не удалось загрузить статистику</p>

        <dl v-else-if="stats">
          <dt>Заявки</dt>
          <dd>{{ stats.submissions_count }}</dd>
          <dt>Голоса</dt>
          <dd>{{ stats.votes_count }}</dd>
          <dt>Участники</dt>
          <dd>{{ stats.participants_count }}</dd>
        </dl>
      </template>
    </template>
  </section>
</template>
