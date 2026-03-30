<script setup lang="ts">
import type { TriageCandidate } from '@/api/types'

defineProps<{
  candidates: TriageCandidate[]
  knownIds: Set<number>
}>()

defineEmits<{
  toggle: [wordId: number]
}>()
</script>

<template>
  <div class="grid grid-cols-2 gap-2 px-4">
    <button
      v-for="c in candidates"
      :key="c.word_id"
      class="flex items-center gap-2 rounded-xl border-2 px-3 py-3 text-left transition-colors"
      :class="
        knownIds.has(c.word_id)
          ? 'border-tg-accent bg-tg-accent/10'
          : 'border-tg-section-separator bg-tg-section-bg'
      "
      @click="$emit('toggle', c.word_id)"
    >
      <span
        class="flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-xs"
        :class="
          knownIds.has(c.word_id)
            ? 'bg-tg-accent text-tg-button-text'
            : 'border border-tg-hint'
        "
      >
        <svg v-if="knownIds.has(c.word_id)" class="h-3 w-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
          <polyline points="20 6 9 17 4 12" />
        </svg>
      </span>
      <div class="min-w-0 flex-1">
        <span class="block text-sm font-medium">{{ c.word }}</span>
        <span v-if="c.definition" class="block truncate text-xs text-tg-hint">{{ c.definition }}</span>
      </div>
    </button>
  </div>
</template>
