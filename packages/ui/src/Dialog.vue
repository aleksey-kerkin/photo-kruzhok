<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from "vue";

import { trapFocus } from "./focusTrap.js";

const props = defineProps({
  open: {
    type: Boolean,
    default: false,
  },
  title: {
    type: String,
    default: undefined,
  },
});

const emit = defineEmits(["close"]);

const dialogRef = ref(null);
let releaseFocus = null;

function syncOpen() {
  const dialog = dialogRef.value;
  if (!dialog) {
    return;
  }

  releaseFocus?.();
  releaseFocus = null;

  if (props.open) {
    if (!dialog.open) {
      dialog.showModal();
    }
    const panel = dialog.querySelector(".pk-dialog__panel");
    releaseFocus = trapFocus(panel ?? dialog);
    return;
  }

  if (dialog.open) {
    dialog.close();
  }
}

function handleClose() {
  emit("close");
}

onMounted(() => {
  dialogRef.value?.addEventListener("close", handleClose);
  syncOpen();
});

watch(() => props.open, syncOpen);

onBeforeUnmount(() => {
  releaseFocus?.();
  dialogRef.value?.removeEventListener("close", handleClose);
});
</script>

<template>
  <dialog ref="dialogRef" class="pk-dialog">
    <div class="pk-dialog__panel">
      <h2 v-if="props.title" class="pk-dialog__title">{{ props.title }}</h2>
      <div class="pk-dialog__body"><slot /></div>
    </div>
  </dialog>
</template>
