import { ref } from 'vue'
import { defineStore } from 'pinia'
import { useUserStore } from './user'
import {
  getTriageCandidates,
  submitTriage as apiSubmitTriage,
  autoSelectDaily,
  getTodayWords,
} from '@/api/daily'
import type { TriageCandidate, WordCard } from '@/api/types'

type DailyState = 'idle' | 'loading' | 'triage' | 'submitting' | 'done' | 'error'

export const useDailyStore = defineStore('daily', () => {
  const state = ref<DailyState>('idle')
  const candidates = ref<TriageCandidate[]>([])
  const sessionId = ref<number | null>(null)
  const knownWordIds = ref<Set<number>>(new Set())
  const dailyWords = ref<WordCard[]>([])
  const sessionDate = ref<string | null>(null)
  const error = ref<string | null>(null)

  async function start() {
    const userStore = useUserStore()
    if (!userStore.telegramId || !userStore.user) return

    state.value = 'loading'
    error.value = null

    try {
      // Check if already done today
      const today = await getTodayWords(userStore.telegramId)
      if (today.status === 'completed' && today.words.length > 0) {
        dailyWords.value = today.words
        sessionDate.value = today.session_date
        state.value = 'done'
        return
      }

      // Auto-select if user prefers skipping triage
      if (userStore.user.skip_triage) {
        const words = await autoSelectDaily(userStore.telegramId)
        dailyWords.value = words
        state.value = 'done'
        return
      }

      // Start triage
      const result = await getTriageCandidates(userStore.telegramId)
      candidates.value = result.candidates
      sessionId.value = result.session_id
      knownWordIds.value = new Set()
      state.value = 'triage'
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to start daily'
      state.value = 'error'
    }
  }

  function toggleKnown(wordId: number) {
    const ids = new Set(knownWordIds.value)
    if (ids.has(wordId)) {
      ids.delete(wordId)
    } else {
      ids.add(wordId)
    }
    knownWordIds.value = ids
  }

  async function submitTriage() {
    const userStore = useUserStore()
    if (!userStore.telegramId || !sessionId.value) return

    state.value = 'submitting'
    error.value = null

    try {
      const known = Array.from(knownWordIds.value)
      const unknown = candidates.value
        .map((c) => c.word_id)
        .filter((id) => !knownWordIds.value.has(id))

      const words = await apiSubmitTriage(userStore.telegramId, {
        session_id: sessionId.value,
        known_word_ids: known,
        unknown_word_ids: unknown,
      })
      dailyWords.value = words
      state.value = 'done'
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to submit triage'
      state.value = 'triage'
    }
  }

  async function skipTriage() {
    const userStore = useUserStore()
    if (!userStore.telegramId) return

    state.value = 'submitting'
    error.value = null

    try {
      const words = await autoSelectDaily(userStore.telegramId)
      dailyWords.value = words
      state.value = 'done'
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to auto-select'
      state.value = 'triage'
    }
  }

  function reset() {
    state.value = 'idle'
    candidates.value = []
    sessionId.value = null
    knownWordIds.value = new Set()
    dailyWords.value = []
    sessionDate.value = null
    error.value = null
  }

  return {
    state, candidates, sessionId, knownWordIds, dailyWords, sessionDate, error,
    start, toggleKnown, submitTriage, skipTriage, reset,
  }
})
