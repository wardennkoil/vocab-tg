import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { useUserStore } from './user'
import { createReviewSession, submitReview, submitReviewBatch, getDueCount } from '@/api/reviews'
import type { ReviewItem } from '@/api/types'

type ReviewState =
  | 'idle'
  | 'loading'
  | 'question'
  | 'feedback'
  | 'submitting'
  | 'summary'

export const useReviewStore = defineStore('review', () => {
  const state = ref<ReviewState>('idle')
  const items = ref<ReviewItem[]>([])
  const currentIndex = ref(0)
  const correctCount = ref(0)
  const totalCount = ref(0)
  const dueCount = ref(0)
  const lastWasCorrect = ref<boolean | null>(null)
  const responseStartTime = ref(0)
  const error = ref<string | null>(null)

  const currentItem = computed(() => items.value[currentIndex.value] ?? null)
  const progress = computed(() => ({
    current: currentIndex.value,
    total: items.value.length,
  }))

  async function fetchDueCount() {
    const userStore = useUserStore()
    if (!userStore.telegramId) return
    try {
      const result = await getDueCount(userStore.telegramId)
      dueCount.value = result.due_count
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch due count'
    }
  }

  async function startSession() {
    const userStore = useUserStore()
    if (!userStore.telegramId) return

    state.value = 'loading'
    error.value = null

    try {
      const session = await createReviewSession(userStore.telegramId)
      items.value = session.items
      totalCount.value = session.total
      dueCount.value = session.due_count
      currentIndex.value = 0
      correctCount.value = 0

      if (items.value.length === 0) {
        state.value = 'summary'
        return
      }

      showCurrentItem()
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to start session'
      state.value = 'idle'
    }
  }

  function showCurrentItem() {
    const item = currentItem.value
    if (!item) {
      state.value = 'summary'
      return
    }
    state.value = 'question'
    responseStartTime.value = Date.now()
  }

  async function submitAnswer(wasCorrect: boolean, extra?: { typedAnswer?: string }) {
    const userStore = useUserStore()
    if (!userStore.telegramId || !currentItem.value) return

    const item = currentItem.value
    const elapsed = Date.now() - responseStartTime.value

    lastWasCorrect.value = wasCorrect
    if (wasCorrect) correctCount.value++
    state.value = 'feedback'

    try {
      await submitReview(userStore.telegramId, {
        user_word_id: item.user_word_id!,
        review_type: item.type,
        was_correct: wasCorrect,
        response_time_ms: elapsed,
        typed_answer: extra?.typedAnswer,
      })
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to submit review'
    }

    setTimeout(() => {
      if (state.value === 'feedback') advance()
    }, 1500)
  }

  async function submitMatchingResult(
    results: { user_word_id: number; was_correct: boolean }[],
  ) {
    const userStore = useUserStore()
    if (!userStore.telegramId) return

    const elapsed = Date.now() - responseStartTime.value
    const correctMatches = results.filter((r) => r.was_correct).length
    correctCount.value += correctMatches
    lastWasCorrect.value = correctMatches === results.length
    state.value = 'feedback'

    try {
      await submitReviewBatch(userStore.telegramId, {
        review_type: 'matching',
        results: results.map((r) => ({
          user_word_id: r.user_word_id,
          review_type: 'matching' as const,
          was_correct: r.was_correct,
        })),
        total_time_ms: elapsed,
      })
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to submit review'
    }

    setTimeout(() => {
      if (state.value === 'feedback') advance()
    }, 2000)
  }

  function advance() {
    currentIndex.value++
    if (currentIndex.value >= items.value.length) {
      state.value = 'summary'
    } else {
      showCurrentItem()
    }
  }

  function reset() {
    state.value = 'idle'
    items.value = []
    currentIndex.value = 0
    correctCount.value = 0
    totalCount.value = 0
    lastWasCorrect.value = null
    error.value = null
  }

  return {
    state, currentItem, progress, correctCount, totalCount, dueCount,
    lastWasCorrect, error,
    fetchDueCount, startSession, submitAnswer, submitMatchingResult, reset,
  }
})
