<script setup lang="ts">
defineProps<{
  message: string
  actionLabel?: string
}>()

defineEmits<{
  action: []
}>()
</script>

<template>
  <div class="flex flex-col items-center justify-center gap-4 px-8 py-16 text-center">
    <slot name="icon" />
    <p class="text-sm text-tg-hint">{{ message }}</p>
    <button
      v-if="actionLabel"
      class="rounded-xl bg-tg-button px-6 py-2.5 text-sm font-medium text-tg-button-text active:opacity-80"
      @click="$emit('action')"
    >
      {{ actionLabel }}
    </button>
  </div>
</template>
