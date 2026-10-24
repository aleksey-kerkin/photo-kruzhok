<template>
  <section>
    <h1>Статистика</h1>

    <p v-if="currentChallengeQuery.isPending.value">Загрузка…</p>
    <p v-else-if="currentForbidden">Недостаточно прав</p>
    <p v-else-if="currentChallengeQuery.isError.value">Не удалось загрузить тему</p>

    <template v-else-if="challenge">
      <p v-if="statsQuery.isPending.value">Загрузка статистики…</p>
      <p v-else-if="statsForbidden">Недостаточно прав</p>
      <p v-else-if="statsQuery.isError.value">Не удалось загрузить статистику</p>

      <dl v-else-if="stats">
        <dt>Заявки</dt>
        <dd>{{ stats.submissions_count }}</dd>
        <dt>Голоса</dt>
        <dd>{{ stats.votes_count }}</dd>
        <dt>Участники</dt>
        <dd>{{ stats.participants_count }}</dd>
      </dl>
    </template>
  </section>
</template>

<script setup>
import { useQuery } from "@tanstack/vue-query";
import { computed } from "vue";

import { isPermissionDenied } from "../api/errors.js";
import { useApiClient } from "../composables/useApiClient.js";

const CURRENT_CHALLENGE_QUERY_KEY = ["challenges", "current"];

const client = useApiClient();

const currentChallengeQuery = useQuery({
  queryKey: CURRENT_CHALLENGE_QUERY_KEY,
  queryFn: () => client.request("/api/challenges/current"),
});

const challenge = computed(() => {
  const data = currentChallengeQuery.data.value;
  if (!data || isPermissionDenied(data)) {
    return null;
  }
  return data;
});

const currentForbidden = computed(() => isPermissionDenied(currentChallengeQuery.data.value));

const challengeId = computed(() => challenge.value?.id ?? null);

const statsQuery = useQuery({
  queryKey: computed(() => ["challenges", challengeId.value, "stats"]),
  enabled: computed(() => challengeId.value != null),
  queryFn: () => client.request(`/api/challenges/${challengeId.value}/stats`),
});

const statsForbidden = computed(() => isPermissionDenied(statsQuery.data.value));

const stats = computed(() => {
  const data = statsQuery.data.value;
  if (!data || isPermissionDenied(data)) {
    return null;
  }
  return data;
});
</script>
