<script setup lang="ts">
import { onMounted } from 'vue'
import { useTelegramBackButton } from '@/composables/useTelegramBackButton'
import { useDailyStore } from '@/stores/daily'
import PageHeader from '@/components/layout/PageHeader.vue'
import LoadingSpinner from '@/components/layout/LoadingSpinner.vue'
import TriageGrid from '@/components/daily/TriageGrid.vue'
import DailyWordSlider from '@/components/daily/DailyWordSlider.vue'

useTelegramBackButton()
const dailyStore = useDailyStore()

onMounted(() => {
  dailyStore.start()
})
</script>

<template>
  <div>
    <PageHeader title="Daily Words" />

    <!-- Loading -->
    <LoadingSpinner v-if="dailyStore.state === 'loading' || dailyStore.state === 'submitting'" />

    <!-- Triage -->
    <div v-else-if="dailyStore.state === 'triage'">
      <p class="mb-4 px-4 text-sm text-tg-hint">
        Tap the words you already know:
      </p>
      <TriageGrid
        :candidates="dailyStore.candidates"
        :known-ids="dailyStore.knownWordIds"
        @toggle="dailyStore.toggleKnown"
      />
      <div class="flex flex-col gap-3 px-4 pt-6">
        <button
          class="w-full rounded-xl bg-tg-button py-3.5 text-center font-medium text-tg-button-text active:opacity-80"
          @click="dailyStore.submitTriage()"
        >
          Done ({{ dailyStore.knownWordIds.size }} known)
        </button>
        <button
          class="text-center text-sm text-tg-accent active:opacity-70"
          @click="dailyStore.skipTriage()"
        >
          Skip — auto-select for me
        </button>
      </div>
    </div>

    <!-- Done -->
    <div v-else-if="dailyStore.state === 'done'">
      <p class="mb-4 px-4 text-sm text-tg-hint">
        {{ dailyStore.sessionDate ? `Words for ${dailyStore.sessionDate}` : "Today's words" }}
        ({{ dailyStore.dailyWords.length }})
      </p>
      <DailyWordSlider :words="dailyStore.dailyWords" />
    </div>

    <!-- Error -->
    <div v-else-if="dailyStore.state === 'error'" class="px-4 py-16 text-center">
      <p class="mb-4 text-sm text-tg-destructive">{{ dailyStore.error }}</p>
      <button
        class="text-sm font-medium text-tg-accent active:opacity-70"
        @click="dailyStore.start()"
      >
        Try again
      </button>
    </div>
  </div>
</template>
