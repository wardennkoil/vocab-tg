<script setup lang="ts">
import { ref } from 'vue'
import type { FillBlankTypeData, WordCard } from '@/api/types'

const props = defineProps<{
  word: WordCard
  fillBlankTypeData: FillBlankTypeData
  disabled?: boolean
  feedbackState?: boolean | null
}>()

const emit = defineEmits<{
  answer: [wasCorrect: boolean, extra: { typedAnswer: string }]
}>()

const input = ref('')

function checkAnswer() {
  const typed = input.value.trim().toLowerCase()
  const correct = props.fillBlankTypeData.correct_answer
  const alternatives = props.fillBlankTypeData.accept_alternatives
  const isCorrect = typed === correct || alternatives.includes(typed)
  emit('answer', isCorrect, { typedAnswer: input.value.trim() })
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && input.value.trim()) {
    checkAnswer()
  }
}
</script>

<template>
  <div class="flex flex-1 flex-col px-4 py-6">
    <p class="mb-2 text-center text-sm text-tg-hint">Type the missing word</p>
    <p class="mb-8 text-center text-base leading-relaxed">
      <template v-for="(part, i) in fillBlankTypeData.sentence_with_blank.split('___')" :key="i">
        <span>{{ part }}</span>
        <span
          v-if="i < fillBlankTypeData.sentence_with_blank.split('___').length - 1"
          class="mx-1 inline-block min-w-[4rem] border-b-2 border-tg-accent"
        >&nbsp;</span>
      </template>
    </p>

    <div v-if="feedbackState != null" class="mb-4 text-center">
      <p
        class="text-sm font-medium"
        :class="feedbackState ? 'text-green-500' : 'text-red-500'"
      >
        {{ feedbackState ? 'Correct!' : `The answer was: ${fillBlankTypeData.correct_answer}` }}
      </p>
    </div>

    <div v-else class="flex gap-3">
      <input
        v-model="input"
        type="text"
        class="flex-1 rounded-xl border-2 border-tg-section-separator bg-tg-secondary-bg px-4 py-3 text-base outline-none focus:border-tg-accent"
        placeholder="Type the word..."
        :disabled="disabled"
        autocomplete="off"
        autocapitalize="off"
        @keydown="handleKeydown"
      />
      <button
        class="rounded-xl bg-tg-button px-6 py-3 font-medium text-tg-button-text active:opacity-80 disabled:opacity-40"
        :disabled="disabled || !input.trim()"
        @click="checkAnswer"
      >
        Check
      </button>
    </div>
  </div>
</template>
