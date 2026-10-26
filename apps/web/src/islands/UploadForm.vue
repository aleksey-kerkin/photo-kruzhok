<script setup>
import { onMounted, ref } from "vue";
import { getAccessToken, restoreAccessToken } from "./session.js";

const sessionLoading = ref(true);
const isAuthenticated = ref(false);
const caption = ref("");
const errorMessage = ref("");

onMounted(() => {
  restoreAccessToken().then((token) => {
    isAuthenticated.value = token != null;
    sessionLoading.value = false;
  });
});

async function onSubmit(event) {
  event.preventDefault();
  errorMessage.value = "";
  const form = event.target;
  const imageInput = form.elements.namedItem("image");
  const file = imageInput instanceof HTMLInputElement ? imageInput.files?.[0] : null;
  if (!file) {
    errorMessage.value = "Выберите снимок";
    return;
  }
  const formData = new FormData();
  formData.append("image", file);
  formData.append("caption", caption.value);
  const response = await fetch("/api/posts", {
    method: "POST",
    headers: { Authorization: `Bearer ${getAccessToken()}` },
    body: formData,
  });
  const body = await response.json();
  if (!response.ok) {
    errorMessage.value = body.message ?? "";
    return;
  }
  window.location.href = `/posts/${body.id}`;
}
</script>

<template>
  <div>
    <p v-if="errorMessage">{{ errorMessage }}</p>
    <p v-if="sessionLoading">Загрузка…</p>
    <template v-else-if="!isAuthenticated">
      <p><a href="/login">Войти, чтобы загрузить снимок</a></p>
    </template>
    <form v-else @submit="onSubmit">
      <label class="pk-field">
        Снимок
        <input class="pk-field__control" name="image" type="file" accept="image/*" />
      </label>
      <label class="pk-field">
        Подпись
        <input class="pk-field__control" v-model="caption" name="caption" type="text" />
      </label>
      <button class="pk-button pk-button--primary" type="submit">Опубликовать</button>
    </form>
  </div>
</template>
