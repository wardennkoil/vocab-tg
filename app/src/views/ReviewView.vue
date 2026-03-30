<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useReviewStore } from '@/stores/review'
import type { ReviewItem } from '@/api/types'
import ReviewProgress from '@/components/review/ReviewProgress.vue'
import ReviewSummary from '@/components/review/ReviewSummary.vue'
import MCQQuestion from '@/components/review/MCQQuestion.vue'
import ReverseMCQ from '@/components/review/ReverseMCQ.vue'
import FillBlankMCQ from '@/components/review/FillBlankMCQ.vue'
import FillBlankType from '@/components/review/FillBlankType.vue'
import MatchingGame from '@/components/review/MatchingGame.vue'
import OddOneOut from '@/components/review/OddOneOut.vue'
import TrueFalse from '@/components/review/TrueFalse.vue'
import WordInContext from '@/components/review/WordInContext.vue'

const router = useRouter()
const store = useReviewStore()

const componentMap: Record<string, unknown> = {
  multiple_choice: MCQQuestion,
  reverse_mcq: ReverseMCQ,
  fill_blank_mcq: FillBlankMCQ,
  fill_blank_type: FillBlankType,
  matching: MatchingGame,
  odd_one_out: OddOneOut,
  true_false: TrueFalse,
  word_in_context: WordInContext,
}

function getComponent(type: string) {
  return componentMap[type] ?? MCQQuestion
}

function getProps(item: ReviewItem) {
  const base = { word: item.word }
  switch (item.type) {
    case 'multiple_choice':
      return { ...base, mcqData: item.mcq_data }
    case 'reverse_mcq':
      return { ...base, reverseMcqData: item.reverse_mcq_data }
    case 'fill_blank_mcq':
      return { ...base, fillBlankMcqData: item.fill_blank_mcq_data }
    case 'fill_blank_type':
      return { ...base, fillBlankTypeData: item.fill_blank_type_data }
    case 'matching':
      return { matchingData: item.matching_data }
    case 'odd_one_out':
      return { ...base, oddOneOutData: item.odd_one_out_data }
    case 'true_false':
      return { ...base, trueFalseData: item.true_false_data }
    case 'word_in_context':
      return { ...base, wordInContextData: item.word_in_context_data }
    default:
      return base
  }
}

function handleAnswer(wasCorrect: boolean, extra?: { typedAnswer?: string }) {
  store.submitAnswer(wasCorrect, extra)
}

onMounted(() => {
  store.fetchDueCount()
})

onUnmounted(() => {
  store.reset()
})

function finishReview() {
  store.reset()
  router.push('/')
}
</script>

<template>
  <div class="flex min-h-screen flex-col">
    <!-- Progress bar (visible during review) -->
    <ReviewProgress
      v-if="!['idle', 'summary', 'loading'].includes(store.state)"
      :current="store.progress.current"
      :total="store.progress.total"
    />

    <!-- IDLE: Start screen -->
    <div v-if="store.state === 'idle'" class="flex flex-1 flex-col items-center justify-center px-6">
      <svg class="mb-4 h-16 w-16 text-tg-accent" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <polyline points="23 4 23 10 17 10" />
        <polyline points="1 20 1 14 7 14" />
        <path d="M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15" />
      </svg>
      <h2 class="mb-2 text-xl font-bold">Review</h2>
      <p class="mb-6 text-sm text-tg-hint">
        {{ store.dueCount > 0 ? `${store.dueCount} words to review` : 'No words due for review' }}
      </p>
      <button
        v-if="store.dueCount > 0"
        class="w-full max-w-xs rounded-xl bg-tg-button py-3.5 text-center font-medium text-tg-button-text active:opacity-80"
        @click="store.startSession()"
      >
        Start Review
      </button>
      <button
        v-else
        class="text-sm text-tg-accent active:opacity-70"
        @click="router.push('/')"
      >
        Back to Home
      </button>
    </div>

    <!-- LOADING -->
    <div v-else-if="store.state === 'loading'" class="flex flex-1 items-center justify-center">
      <div class="h-8 w-8 animate-spin rounded-full border-3 border-tg-secondary-bg border-t-tg-accent" />
    </div>

    <!-- QUESTION / FEEDBACK -->
    <component
      v-else-if="['question', 'feedback'].includes(store.state) && store.currentItem"
      :is="getComponent(store.currentItem.type)"
      :key="store.progress.current"
      v-bind="getProps(store.currentItem)"
      :disabled="store.state === 'feedback'"
      :feedback-state="store.state === 'feedback' ? store.lastWasCorrect : null"
      @answer="handleAnswer"
      @complete="store.submitMatchingResult"
    />

    <!-- SUBMITTING -->
    <div v-else-if="store.state === 'submitting'" class="flex flex-1 items-center justify-center">
      <div class="h-6 w-6 animate-spin rounded-full border-2 border-tg-secondary-bg border-t-tg-accent" />
    </div>

    <!-- SUMMARY -->
    <ReviewSummary
      v-else-if="store.state === 'summary'"
      :correct="store.correctCount"
      :total="store.totalCount"
      @done="finishReview"
    />

    <!-- Error -->
    <div v-if="store.error" class="px-4 py-4 text-center text-sm text-tg-destructive">
      {{ store.error }}
    </div>
  </div>
</template>
