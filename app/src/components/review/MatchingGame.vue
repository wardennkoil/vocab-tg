<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { MatchingData } from '@/api/types'

const props = defineProps<{
  matchingData: MatchingData
  disabled?: boolean
  feedbackState?: boolean | null
}>()

const emit = defineEmits<{
  complete: [results: { user_word_id: number; was_correct: boolean }[]]
}>()

interface ShuffledWord {
  user_word_id: number
  word: string
  index: number
}

interface ShuffledDef {
  user_word_id: number
  definition: string
  index: number
}

const shuffledWords = ref<ShuffledWord[]>([])
const shuffledDefs = ref<ShuffledDef[]>([])
const selectedWordIdx = ref<number | null>(null)
const matches = ref<Map<number, { defIdx: number; correct: boolean }>>(new Map())

onMounted(() => {
  const words = props.matchingData.pairs.map((p, i) => ({
    user_word_id: p.user_word_id,
    word: p.word,
    index: i,
  }))
  const defs = props.matchingData.pairs.map((p, i) => ({
    user_word_id: p.user_word_id,
    definition: p.definition,
    index: i,
  }))
  // Shuffle both arrays independently
  for (let i = words.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[words[i], words[j]] = [words[j], words[i]]
  }
  for (let i = defs.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[defs[i], defs[j]] = [defs[j], defs[i]]
  }
  shuffledWords.value = words
  shuffledDefs.value = defs
})

function isWordMatched(wordIdx: number) {
  return matches.value.has(wordIdx)
}

function isDefMatched(defIdx: number) {
  for (const m of matches.value.values()) {
    if (m.defIdx === defIdx) return true
  }
  return false
}

function selectWord(wordIdx: number) {
  if (props.disabled || isWordMatched(wordIdx)) return
  selectedWordIdx.value = wordIdx
}

function selectDef(defIdx: number) {
  if (props.disabled || selectedWordIdx.value === null || isDefMatched(defIdx)) return

  const wordItem = shuffledWords.value[selectedWordIdx.value]
  const defItem = shuffledDefs.value[defIdx]
  const correct = wordItem.user_word_id === defItem.user_word_id

  const newMatches = new Map(matches.value)
  newMatches.set(selectedWordIdx.value, { defIdx, correct })
  matches.value = newMatches
  selectedWordIdx.value = null

  if (newMatches.size === props.matchingData.pairs.length) {
    const results = shuffledWords.value.map((w, wIdx) => ({
      user_word_id: w.user_word_id,
      was_correct: newMatches.get(wIdx)?.correct ?? false,
    }))
    emit('complete', results)
  }
}

function wordClass(wordIdx: number) {
  const match = matches.value.get(wordIdx)
  if (match) {
    if (props.feedbackState != null) {
      return match.correct
        ? 'border-green-500 bg-green-500/10'
        : 'border-red-500 bg-red-500/10'
    }
    return 'border-tg-accent/50 bg-tg-accent/5'
  }
  if (selectedWordIdx.value === wordIdx) return 'border-tg-accent bg-tg-accent/10'
  return 'border-tg-section-separator active:bg-tg-secondary-bg'
}

function defClass(defIdx: number) {
  for (const [, m] of matches.value) {
    if (m.defIdx === defIdx) {
      if (props.feedbackState != null) {
        return m.correct
          ? 'border-green-500 bg-green-500/10'
          : 'border-red-500 bg-red-500/10'
      }
      return 'border-tg-accent/50 bg-tg-accent/5'
    }
  }
  if (selectedWordIdx.value !== null && !isDefMatched(defIdx)) {
    return 'border-tg-section-separator active:bg-tg-accent/10'
  }
  return 'border-tg-section-separator'
}
</script>

<template>
  <div class="flex flex-1 flex-col px-4 py-6">
    <p class="mb-2 text-center text-sm text-tg-hint">Match each word with its definition</p>
    <p class="mb-6 text-center text-xs text-tg-subtitle">Tap a word, then tap its definition</p>

    <div class="grid grid-cols-2 gap-3">
      <!-- Words column -->
      <div class="flex flex-col gap-2">
        <button
          v-for="(w, i) in shuffledWords"
          :key="'w-' + i"
          class="rounded-xl border-2 px-3 py-3 text-center text-sm font-medium transition-colors"
          :class="wordClass(i)"
          :disabled="disabled || isWordMatched(i)"
          @click="selectWord(i)"
        >
          {{ w.word }}
        </button>
      </div>

      <!-- Definitions column -->
      <div class="flex flex-col gap-2">
        <button
          v-for="(d, i) in shuffledDefs"
          :key="'d-' + i"
          class="rounded-xl border-2 px-3 py-3 text-left text-xs leading-snug transition-colors"
          :class="defClass(i)"
          :disabled="disabled || isDefMatched(i) || selectedWordIdx === null"
          @click="selectDef(i)"
        >
          {{ d.definition }}
        </button>
      </div>
    </div>
  </div>
</template>
