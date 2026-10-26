<script setup>
import { ref } from "vue";
import { getAccessToken, restoreAccessToken } from "./session.js";

const props = defineProps({
  postId: {
    type: String,
    required: true,
  },
  liked: {
    type: Boolean,
    required: true,
  },
  likesCount: {
    type: Number,
    required: true,
  },
});

const isAuthenticated = ref(false);
const liked = ref(props.liked);
const likesCount = ref(props.likesCount);
const commentText = ref("");
const errorMessage = ref("");

restoreAccessToken().then((token) => {
  isAuthenticated.value = token != null;
});

async function toggleLike() {
  errorMessage.value = "";
  const method = liked.value ? "DELETE" : "PUT";
  const response = await fetch(`/api/posts/${props.postId}/like`, {
    method,
    headers: { Authorization: `Bearer ${getAccessToken()}` },
  });
  const body = await response.json();
  if (!response.ok) {
    errorMessage.value = body.message ?? "";
    return;
  }
  liked.value = !liked.value;
  likesCount.value += liked.value ? 1 : -1;
}

async function onCommentSubmit(event) {
  event.preventDefault();
  errorMessage.value = "";
  const response = await fetch(`/api/posts/${props.postId}/comments`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${getAccessToken()}`,
    },
    body: JSON.stringify({ text: commentText.value }),
  });
  const body = await response.json();
  if (!response.ok) {
    errorMessage.value = body.message ?? "";
    return;
  }
  commentText.value = "";
}
</script>

<template>
  <div>
    <p v-if="errorMessage">{{ errorMessage }}</p>
    <template v-if="!isAuthenticated">
      <p><a href="/login">Войти, чтобы оценить</a></p>
      <p><a href="/login">Войти, чтобы комментировать</a></p>
    </template>
    <template v-else>
      <p>
        <button type="button" @click="toggleLike">Лайк</button>
        {{ likesCount }}
      </p>
      <form @submit="onCommentSubmit">
        <label>
          Комментарий
          <input v-model="commentText" name="text" type="text" />
        </label>
        <button type="submit">Отправить</button>
      </form>
    </template>
  </div>
</template>
