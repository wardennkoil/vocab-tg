<script setup lang="ts">
import type { WordCard } from '@/api/types'
import AudioButton from './AudioButton.vue'

defineProps<{
  word: WordCard
}>()
</script>

<template>
  <div class="rounded-2xl bg-tg-section-bg p-4">
    <!-- Word + Phonetic -->
    <div class="mb-3 flex items-center gap-2">
      <h2 class="text-2xl font-bold">{{ word.word }}</h2>
      <AudioButton v-if="word.audio_url" :url="word.audio_url" />
    </div>
    <div class="mb-3 flex flex-wrap items-center gap-2">
      <span v-if="word.phonetic" class="text-sm text-tg-hint">{{ word.phonetic }}</span>
      <span
        v-if="word.part_of_speech"
        class="rounded-full bg-tg-secondary-bg px-2 py-0.5 text-xs text-tg-subtitle"
      >
        {{ word.part_of_speech }}
      </span>
      <span
        v-if="word.difficulty_band"
        class="rounded-full bg-tg-secondary-bg px-2 py-0.5 text-xs text-tg-hint"
      >
        {{ word.difficulty_band }}
      </span>
    </div>

    <!-- Definition -->
    <p v-if="word.definition" class="mb-2 text-sm leading-relaxed">
      {{ word.definition }}
    </p>

    <!-- Translation -->
    <p v-if="word.translation_ru" class="mb-3 text-sm text-tg-hint">
      {{ word.translation_ru }}
    </p>

    <!-- Example -->
    <p v-if="word.example_sentence" class="mb-3 border-l-2 border-tg-accent pl-3 text-sm italic text-tg-subtitle">
      {{ word.example_sentence }}
    </p>

    <!-- Synonyms -->
    <div v-if="word.synonyms.length > 0" class="mb-2">
      <span class="text-xs font-medium text-tg-section-header">Synonyms:</span>
      <div class="mt-1 flex flex-wrap gap-1.5">
        <span
          v-for="syn in word.synonyms"
          :key="syn"
          class="rounded-full bg-tg-secondary-bg px-2.5 py-0.5 text-xs"
        >
          {{ syn }}
        </span>
      </div>
    </div>

    <!-- Antonyms -->
    <div v-if="word.antonyms.length > 0">
      <span class="text-xs font-medium text-tg-section-header">Antonyms:</span>
      <div class="mt-1 flex flex-wrap gap-1.5">
        <span
          v-for="ant in word.antonyms"
          :key="ant"
          class="rounded-full bg-tg-secondary-bg px-2.5 py-0.5 text-xs"
        >
          {{ ant }}
        </span>
      </div>
    </div>
  </div>
</template>
