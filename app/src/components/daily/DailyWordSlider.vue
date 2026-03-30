<script setup lang="ts">
import type { WordCard } from '@/api/types'
import WordCardComponent from '@/components/word/WordCard.vue'

defineProps<{
  words: WordCard[]
}>()
</script>

<template>
  <div class="flex snap-x snap-mandatory gap-4 overflow-x-auto px-4 pb-4 scrollbar-none">
    <div
      v-for="word in words"
      :key="word.id"
      class="w-[calc(100%-2rem)] shrink-0 snap-center"
    >
      <WordCardComponent :word="word" />
    </div>
  </div>
</template>

<style scoped>
.scrollbar-none::-webkit-scrollbar {
  display: none;
}
.scrollbar-none {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
