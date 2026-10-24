<template>
  <section>
    <h1>Тема</h1>

    <p v-if="currentChallengeQuery.isPending.value">Загрузка…</p>
    <p v-else-if="forbidden">Недостаточно прав</p>
    <p v-else-if="currentChallengeQuery.isError.value">Не удалось загрузить тему</p>

    <template v-else-if="challenge">
      <h2>{{ challenge.title }}</h2>
      <p v-if="challenge.description">{{ challenge.description }}</p>
      <p>
        <span>Статус: {{ challenge.status }}</span>
      </p>

      <h3>Заявки</h3>
      <p v-if="submissionsQuery.isPending.value">Загрузка заявок…</p>
      <p v-else-if="submissionsForbidden">Недостаточно прав</p>
      <ul v-else-if="submissions.length">
        <li v-for="submission in submissions" :key="submission.id">
          <span>{{ submissionCaption(submission) }}</span>
          <button
            type="button"
            :disabled="voteMutation.isPending.value"
            @click="voteMutation.mutate(submission.id)"
          >
            Проголосовать
          </button>
        </li>
      </ul>
      <p v-else>Заявок пока нет</p>
    </template>
  </section>
</template>

<script setup>
import { useMutation, useQuery, useQueryClient } from "@tanstack/vue-query";
import { computed } from "vue";

import { isPermissionDenied } from "../api/errors.js";
import { useApiClient } from "../composables/useApiClient.js";

const CURRENT_CHALLENGE_QUERY_KEY = ["challenges", "current"];

const client = useApiClient();
const queryClient = useQueryClient();

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

const forbidden = computed(() => isPermissionDenied(currentChallengeQuery.data.value));

const challengeId = computed(() => challenge.value?.id ?? null);

const submissionsQuery = useQuery({
  queryKey: computed(() => ["challenges", challengeId.value, "submissions"]),
  enabled: computed(() => challengeId.value != null),
  queryFn: () => client.request(`/api/challenges/${challengeId.value}/submissions`),
});

const submissionsForbidden = computed(() => isPermissionDenied(submissionsQuery.data.value));

const submissions = computed(() => {
  const data = submissionsQuery.data.value;
  if (!data || isPermissionDenied(data)) {
    return [];
  }
  return data.results ?? [];
});

function submissionCaption(submission) {
  const caption = submission.post?.caption;
  if (caption) {
    return caption;
  }
  return `Заявка ${submission.id}`;
}

const voteMutation = useMutation({
  mutationFn: (submissionId) =>
    client.request(`/api/challenges/${challengeId.value}/votes`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ submission_id: submissionId }),
    }),
  onSuccess: () => {
    if (challengeId.value != null) {
      queryClient.invalidateQueries({
        queryKey: ["challenges", challengeId.value, "submissions"],
      });
    }
  },
});
</script>
