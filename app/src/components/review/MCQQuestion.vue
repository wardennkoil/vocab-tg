<script setup lang="ts">
import type { MCQData, WordCard } from '@/api/types'

const props = defineProps<{
  word: WordCard
  mcqData: MCQData
  disabled?: boolean
  feedbackState?: boolean | null
}>()

const emit = defineEmits<{
  answer: [wasCorrect: boolean]
}>()

function optionClass(index: number) {
  if (props.disabled && props.feedbackState != null) {
    if (index === props.mcqData.correct_index) return 'border-green-500 bg-green-500/10'
    if (props.feedbackState === false) return 'border-red-500/30'
  }
  return 'border-tg-section-separator active:bg-tg-secondary-bg'
}

function handleAnswer(index: number) {
  emit('answer', index === props.mcqData.correct_index)
}
</script>

<template>
  <div class="flex flex-1 flex-col px-4 py-6">
    <p class="mb-2 text-center text-sm text-tg-hint">Which word matches this definition?</p>
    <p class="mb-8 text-center text-base font-medium leading-relaxed">
      {{ word.definition || word.translation_ru || '—' }}
    </p>
    <div class="flex flex-col gap-3">
      <button
        v-for="(option, i) in mcqData.options"
        :key="option.id"
        class="rounded-xl border-2 px-4 py-3.5 text-left text-base font-medium transition-colors"
        :class="optionClass(i)"
        :disabled="disabled"
        @click="handleAnswer(i)"
      >
        {{ option.word }}
      </button>
    </div>
  </div>
</template>
