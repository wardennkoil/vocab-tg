<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  correct: number
  total: number
}>()

defineEmits<{
  done: []
}>()

const accuracy = computed(() =>
  props.total > 0 ? Math.round((props.correct / props.total) * 100) : 0,
)
</script>

<template>
  <div class="flex flex-1 flex-col items-center justify-center px-6">
    <div class="mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-green-500/10">
      <svg class="h-10 w-10 text-green-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <polyline points="20 6 9 17 4 12" />
      </svg>
    </div>
    <h2 class="mb-2 text-2xl font-bold">Session Complete</h2>
    <p class="mb-1 text-lg text-tg-hint">
      {{ correct }} / {{ total }} correct
    </p>
    <p class="mb-8 text-3xl font-bold text-tg-accent">{{ accuracy }}%</p>
    <button
      class="w-full max-w-xs rounded-xl bg-tg-button py-3.5 text-center font-medium text-tg-button-text active:opacity-80"
      @click="$emit('done')"
    >
      Back to Home
    </button>
  </div>
</template>
