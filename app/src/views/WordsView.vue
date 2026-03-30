<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useWordsStore } from '@/stores/words'
import PageHeader from '@/components/layout/PageHeader.vue'
import WordCardCompact from '@/components/word/WordCardCompact.vue'
import EmptyState from '@/components/layout/EmptyState.vue'

const router = useRouter()
const wordsStore = useWordsStore()
const sentinelRef = ref<HTMLElement | null>(null)

const filters = [
  { value: null, label: 'All' },
  { value: 'learning', label: 'Learning' },
  { value: 'reviewing', label: 'Reviewing' },
  { value: 'known', label: 'Known' },
  { value: 'custom', label: 'Custom' },
]

onMounted(() => {
  wordsStore.fetchPage(1)

  // Infinite scroll
  if (sentinelRef.value) {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && !wordsStore.loading) {
          wordsStore.loadMore()
        }
      },
      { rootMargin: '200px' },
    )
    observer.observe(sentinelRef.value)
  }
})
</script>

<template>
  <div>
    <PageHeader title="My Words" />

    <!-- Filter chips -->
    <div class="flex gap-2 overflow-x-auto px-4 pb-3 scrollbar-none">
      <button
        v-for="f in filters"
        :key="String(f.value)"
        class="shrink-0 rounded-full px-3 py-1.5 text-xs font-medium transition-colors"
        :class="
          wordsStore.statusFilter === f.value
            ? 'bg-tg-accent text-tg-button-text'
            : 'bg-tg-secondary-bg text-tg-text'
        "
        @click="wordsStore.setFilter(f.value)"
      >
        {{ f.label }}
      </button>
    </div>

    <!-- Word list -->
    <div v-if="wordsStore.items.length > 0" class="flex flex-col gap-2 px-4">
      <WordCardCompact
        v-for="uw in wordsStore.items"
        :key="uw.id"
        :user-word="uw"
        @click="router.push(`/words/${encodeURIComponent(uw.word.word)}`)"
      />
      <div ref="sentinelRef" class="h-4" />
    </div>

    <EmptyState
      v-else-if="!wordsStore.loading"
      message="No words found. Add some words to get started!"
      action-label="Add a Word"
      @action="router.push('/add')"
    />

    <!-- Loading -->
    <div v-if="wordsStore.loading" class="flex justify-center py-6">
      <div class="h-6 w-6 animate-spin rounded-full border-2 border-tg-secondary-bg border-t-tg-accent" />
    </div>

    <!-- FAB -->
    <button
      class="fixed right-4 bottom-24 z-40 flex h-14 w-14 items-center justify-center rounded-full bg-tg-button shadow-lg active:opacity-80"
      @click="router.push('/add')"
    >
      <svg class="h-6 w-6 text-tg-button-text" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <line x1="12" y1="5" x2="12" y2="19" />
        <line x1="5" y1="12" x2="19" y2="12" />
      </svg>
    </button>
  </div>
</template>

<style scoped>
.scrollbar-none::-webkit-scrollbar { display: none; }
.scrollbar-none { -ms-overflow-style: none; scrollbar-width: none; }
</style>
