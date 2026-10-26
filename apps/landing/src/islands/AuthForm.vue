<script setup>
import { computed, ref } from "vue";
import { login, register } from "./session.js";

const props = defineProps({
  mode: {
    type: String,
    required: true,
    validator: (value) => value === "login" || value === "register",
  },
});

const username = ref("");
const email = ref("");
const password = ref("");
const fieldErrors = ref({});

const submitLabel = computed(() =>
  props.mode === "login" ? "Войти" : "Создать аккаунт",
);

async function onSubmit(event) {
  event.preventDefault();
  fieldErrors.value = {};

  const result =
    props.mode === "login"
      ? await login({ username: username.value, password: password.value })
      : await register({
          username: username.value,
          email: email.value,
          password: password.value,
        });

  if (result.ok) {
    window.location.assign("/");
    return;
  }

  if (result.body.fields) {
    fieldErrors.value = result.body.fields;
  }
}
</script>

<template>
  <form @submit="onSubmit">
    <label>
      Имя
      <input v-model="username" name="username" type="text" autocomplete="username" />
      <span v-if="fieldErrors.username">{{ fieldErrors.username }}</span>
    </label>
    <label v-if="mode === 'register'">
      Почта
      <input v-model="email" name="email" type="email" autocomplete="email" />
      <span v-if="fieldErrors.email">{{ fieldErrors.email }}</span>
    </label>
    <label>
      Пароль
      <input
        v-model="password"
        name="password"
        type="password"
        :autocomplete="mode === 'login' ? 'current-password' : 'new-password'"
      />
      <span v-if="fieldErrors.password">{{ fieldErrors.password }}</span>
    </label>
    <button type="submit">{{ submitLabel }}</button>
  </form>
</template>
