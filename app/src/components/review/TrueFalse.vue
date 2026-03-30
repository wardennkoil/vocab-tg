<script setup lang="ts">
import type { TrueFalseData, WordCard } from '@/api/types'

const props = defineProps<{
  word: WordCard
  trueFalseData: TrueFalseData
  disabled?: boolean
  feedbackState?: boolean | null
}>()

const emit = defineEmits<{
  answer: [wasCorrect: boolean]
}>()

function handleAnswer(userSaidCorrect: boolean) {
  const wasCorrect = userSaidCorrect === props.trueFalseData.is_correct_pair
  emit('answer', wasCorrect)
}

function buttonClass(isCorrectBtn: boolean) {
  if (props.disabled && props.feedbackState != null) {
    const correctAnswer = props.trueFalseData.is_correct_pair
    if (isCorrectBtn === correctAnswer) return 'border-green-500 bg-green-500/10'
    if (props.feedbackState === false) return 'border-red-500/30'
  }
  return isCorrectBtn
    ? 'border-green-500/30 active:bg-green-500/10'
    : 'border-red-500/30 active:bg-red-500/10'
}
</script>

<template>
  <div class="flex flex-1 flex-col px-4 py-6">
    <p class="mb-2 text-center text-sm text-tg-hint">Is this definition correct?</p>
    <p class="mb-4 text-center text-2xl font-bold">{{ word.word }}</p>
    <p class="mb-8 text-center text-base leading-relaxed text-tg-subtitle">
      {{ trueFalseData.shown_definition }}
    </p>
    <div class="flex gap-3">
      <button
        class="flex-1 rounded-xl border-2 py-4 text-center text-base font-medium transition-colors"
        :class="buttonClass(true)"
        :disabled="disabled"
        @click="handleAnswer(true)"
      >
        Correct
      </button>
      <button
        class="flex-1 rounded-xl border-2 py-4 text-center text-base font-medium transition-colors"
        :class="buttonClass(false)"
        :disabled="disabled"
        @click="handleAnswer(false)"
      >
        Wrong
      </button>
    </div>
  </div>
</template>
