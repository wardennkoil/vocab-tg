<script setup lang="ts">
import type { UserWordResponse } from '@/api/types'
import WordStatusBadge from './WordStatusBadge.vue'

defineProps<{
  userWord: UserWordResponse
}>()

defineEmits<{
  click: []
}>()
</script>

<template>
  <button
    class="flex w-full items-center gap-3 rounded-xl bg-tg-section-bg px-4 py-3 text-left active:opacity-80"
    @click="$emit('click')"
  >
    <div class="min-w-0 flex-1">
      <div class="flex items-center gap-2">
        <span class="text-base font-medium">{{ userWord.word.word }}</span>
        <span
          v-if="userWord.word.part_of_speech"
          class="shrink-0 text-xs text-tg-hint"
        >
          {{ userWord.word.part_of_speech }}
        </span>
      </div>
      <p v-if="userWord.word.definition" class="mt-0.5 truncate text-xs text-tg-hint">
        {{ userWord.word.definition }}
      </p>
    </div>
    <WordStatusBadge :status="userWord.status" />
    <svg class="h-4 w-4 shrink-0 text-tg-hint" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <polyline points="9 18 15 12 9 6" />
    </svg>
  </button>
</template>
