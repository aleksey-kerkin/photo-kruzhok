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
    <label class="pk-field">
      Имя
      <input class="pk-field__control" v-model="username" name="username" type="text" autocomplete="username" />
      <span class="pk-field__error" v-if="fieldErrors.username">{{ fieldErrors.username }}</span>
    </label>
    <label class="pk-field" v-if="mode === 'register'">
      Почта
      <input class="pk-field__control" v-model="email" name="email" type="email" autocomplete="email" />
      <span class="pk-field__error" v-if="fieldErrors.email">{{ fieldErrors.email }}</span>
    </label>
    <label class="pk-field">
      Пароль
      <input
        class="pk-field__control"
        v-model="password"
        name="password"
        type="password"
        :autocomplete="mode === 'login' ? 'current-password' : 'new-password'"
      />
      <span class="pk-field__error" v-if="fieldErrors.password">{{ fieldErrors.password }}</span>
    </label>
    <button class="pk-button pk-button--primary" type="submit">{{ submitLabel }}</button>
  </form>
</template>
