<script setup lang="ts">
import type { WordInContextData, WordCard } from '@/api/types'

const props = defineProps<{
  word: WordCard
  wordInContextData: WordInContextData
  disabled?: boolean
  feedbackState?: boolean | null
}>()

const emit = defineEmits<{
  answer: [wasCorrect: boolean]
}>()

function optionClass(index: number) {
  if (props.disabled && props.feedbackState != null) {
    if (index === props.wordInContextData.correct_index) return 'border-green-500 bg-green-500/10'
    if (props.feedbackState === false) return 'border-red-500/30'
  }
  return 'border-tg-section-separator active:bg-tg-secondary-bg'
}

function handleAnswer(index: number) {
  emit('answer', index === props.wordInContextData.correct_index)
}
</script>

<template>
  <div class="flex flex-1 flex-col px-4 py-6">
    <p class="mb-2 text-center text-sm text-tg-hint">
      What does <span class="font-bold text-tg-accent">{{ word.word }}</span> mean here?
    </p>
    <p class="mb-8 rounded-xl bg-tg-secondary-bg p-4 text-center text-base leading-relaxed">
      {{ wordInContextData.sentence }}
    </p>
    <div class="flex flex-col gap-3">
      <button
        v-for="(def, i) in wordInContextData.definition_options"
        :key="i"
        class="rounded-xl border-2 px-4 py-3.5 text-left text-sm leading-relaxed transition-colors"
        :class="optionClass(i)"
        :disabled="disabled"
        @click="handleAnswer(i)"
      >
        {{ def }}
      </button>
    </div>
  </div>
</template>
