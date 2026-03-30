<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTelegramBackButton } from '@/composables/useTelegramBackButton'
import { getWordCard } from '@/api/words'
import { useWordsStore } from '@/stores/words'
import type { WordCard } from '@/api/types'
import WordCardComponent from '@/components/word/WordCard.vue'
import PageHeader from '@/components/layout/PageHeader.vue'

useTelegramBackButton()

const route = useRoute()
const router = useRouter()
const wordsStore = useWordsStore()

const word = ref<WordCard | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)
const deleting = ref(false)

const wordParam = route.params.word as string

// Find if this word is in the user's list
const userWord = wordsStore.items.find(
  (w) => w.word.word === wordParam,
)

onMounted(async () => {
  try {
    word.value = await getWordCard(wordParam)
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Failed to load word'
  } finally {
    loading.value = false
  }
})

async function handleDelete() {
  if (!userWord || deleting.value) return
  deleting.value = true
  await wordsStore.deleteWord(userWord.id)
  router.back()
}
</script>

<template>
  <div>
    <PageHeader :title="wordParam" />

    <div v-if="loading" class="flex justify-center py-16">
      <div class="h-6 w-6 animate-spin rounded-full border-2 border-tg-secondary-bg border-t-tg-accent" />
    </div>

    <div v-else-if="error" class="px-4 py-16 text-center text-sm text-tg-destructive">
      {{ error }}
    </div>

    <div v-else-if="word" class="px-4 pb-8">
      <WordCardComponent :word="word" />

      <button
        v-if="userWord"
        class="mt-4 w-full rounded-xl bg-tg-destructive/10 py-3 text-center text-sm font-medium text-tg-destructive active:opacity-70"
        :disabled="deleting"
        @click="handleDelete"
      >
        {{ deleting ? 'Removing...' : 'Remove from my list' }}
      </button>
    </div>
  </div>
</template>
