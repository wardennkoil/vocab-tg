<script setup lang="ts">
import { ref, watch } from 'vue'
import { useTelegramBackButton } from '@/composables/useTelegramBackButton'
import { useDebounce } from '@/composables/useDebounce'
import { searchWords, getWordCard } from '@/api/words'
import { useWordsStore } from '@/stores/words'
import type { WordCard, WordSuggestion } from '@/api/types'
import PageHeader from '@/components/layout/PageHeader.vue'
import WordCardComponent from '@/components/word/WordCard.vue'

useTelegramBackButton()
const wordsStore = useWordsStore()

const query = ref('')
const debouncedQuery = useDebounce(query, 300)
const suggestions = ref<WordSuggestion[]>([])
const preview = ref<WordCard | null>(null)
const searching = ref(false)
const adding = ref(false)
const added = ref(false)
const error = ref<string | null>(null)

watch(debouncedQuery, async (q) => {
  preview.value = null
  added.value = false
  error.value = null
  if (!q || q.length < 2) {
    suggestions.value = []
    return
  }
  searching.value = true
  try {
    suggestions.value = await searchWords(q)
  } catch {
    suggestions.value = []
  } finally {
    searching.value = false
  }
})

async function selectSuggestion(word: string) {
  query.value = word
  suggestions.value = []
  error.value = null
  searching.value = true
  try {
    preview.value = await getWordCard(word)
  } catch {
    error.value = 'Could not load word details'
  } finally {
    searching.value = false
  }
}

async function handleAdd() {
  if (!preview.value || adding.value) return
  adding.value = true
  error.value = null
  try {
    await wordsStore.addWord(preview.value.word)
    added.value = true
  } catch {
    error.value = 'Failed to add word'
  } finally {
    adding.value = false
  }
}

function reset() {
  query.value = ''
  preview.value = null
  suggestions.value = []
  added.value = false
  error.value = null
}
</script>

<template>
  <div>
    <PageHeader title="Add Word" />

    <div class="px-4">
      <!-- Search -->
      <div class="relative mb-4">
        <input
          v-model="query"
          type="text"
          placeholder="Search for a word..."
          class="w-full rounded-xl bg-tg-secondary-bg px-4 py-3 text-sm placeholder:text-tg-hint focus:ring-2 focus:ring-tg-accent"
        />
        <div
          v-if="searching"
          class="absolute right-3 top-1/2 -translate-y-1/2"
        >
          <div class="h-4 w-4 animate-spin rounded-full border-2 border-tg-hint border-t-tg-accent" />
        </div>
      </div>

      <!-- Suggestions -->
      <div
        v-if="suggestions.length > 0 && !preview"
        class="mb-4 divide-y divide-tg-section-separator rounded-xl bg-tg-section-bg"
      >
        <button
          v-for="s in suggestions"
          :key="s.word"
          class="w-full px-4 py-3 text-left text-sm active:bg-tg-secondary-bg"
          @click="selectSuggestion(s.word)"
        >
          {{ s.word }}
        </button>
      </div>

      <!-- Preview -->
      <div v-if="preview && !added">
        <WordCardComponent :word="preview" class="mb-4" />
        <button
          class="w-full rounded-xl bg-tg-button py-3.5 text-center font-medium text-tg-button-text active:opacity-80"
          :disabled="adding"
          @click="handleAdd"
        >
          {{ adding ? 'Adding...' : 'Add to My Words' }}
        </button>
      </div>

      <!-- Added success -->
      <div v-if="added" class="mt-4 rounded-xl bg-green-500/10 p-4 text-center">
        <p class="mb-3 text-sm font-medium text-green-600">Word added successfully!</p>
        <button
          class="text-sm font-medium text-tg-accent active:opacity-70"
          @click="reset"
        >
          Add another word
        </button>
      </div>

      <!-- Error -->
      <p v-if="error" class="mt-3 text-center text-sm text-tg-destructive">{{ error }}</p>
    </div>
  </div>
</template>
