<script setup>
const props = defineProps({
  variant: {
    type: String,
    default: undefined,
  },
  type: {
    type: String,
    default: "button",
  },
});
</script>

<template>
  <button
    :type="props.type"
    :class="['pk-button', props.variant === 'primary' ? 'pk-button--primary' : null]"
  >
    <span class="pk-button__label"><slot /></span>
  </button>
</template>
