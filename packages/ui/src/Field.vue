<script setup>
const props = defineProps({
  id: {
    type: String,
    required: true,
  },
  label: {
    type: String,
    required: true,
  },
  error: {
    type: String,
    default: undefined,
  },
  invalid: {
    type: Boolean,
    default: false,
  },
});

const errorId = props.error ? `${props.id}-error` : undefined;
</script>

<template>
  <div :class="['pk-field', props.invalid || props.error ? 'pk-field--invalid' : null]">
    <label class="pk-field__label" :for="props.id">{{ props.label }}</label>
    <input
      :id="props.id"
      class="pk-field__control"
      :aria-invalid="props.invalid || Boolean(props.error) || undefined"
      :aria-describedby="errorId"
      v-bind="$attrs"
    />
    <p v-if="props.error" :id="errorId" class="pk-field__error" role="alert">{{ props.error }}</p>
  </div>
</template>
