<script setup lang="ts">
import type { FillBlankMCQData, WordCard } from '@/api/types'

const props = defineProps<{
  word: WordCard
  fillBlankMcqData: FillBlankMCQData
  disabled?: boolean
  feedbackState?: boolean | null
}>()

const emit = defineEmits<{
  answer: [wasCorrect: boolean]
}>()

function optionClass(index: number) {
  if (props.disabled && props.feedbackState != null) {
    if (index === props.fillBlankMcqData.correct_index) return 'border-green-500 bg-green-500/10'
    if (props.feedbackState === false) return 'border-red-500/30'
  }
  return 'border-tg-section-separator active:bg-tg-secondary-bg'
}

function handleAnswer(index: number) {
  emit('answer', index === props.fillBlankMcqData.correct_index)
}
</script>

<template>
  <div class="flex flex-1 flex-col px-4 py-6">
    <p class="mb-2 text-center text-sm text-tg-hint">Complete the sentence</p>
    <p class="mb-8 text-center text-base leading-relaxed">
      <template v-for="(part, i) in fillBlankMcqData.sentence_with_blank.split('___')" :key="i">
        <span>{{ part }}</span>
        <span
          v-if="i < fillBlankMcqData.sentence_with_blank.split('___').length - 1"
          class="mx-1 inline-block min-w-[4rem] border-b-2 border-tg-accent"
        >&nbsp;</span>
      </template>
    </p>
    <div class="flex flex-col gap-3">
      <button
        v-for="(option, i) in fillBlankMcqData.options"
        :key="i"
        class="rounded-xl border-2 px-4 py-3.5 text-left text-base font-medium transition-colors"
        :class="optionClass(i)"
        :disabled="disabled"
        @click="handleAnswer(i)"
      >
        {{ option }}
      </button>
    </div>
  </div>
</template>
