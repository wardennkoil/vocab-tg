<script setup lang="ts">
import type { StatsOverview } from '@/api/types'
import StatCard from './StatCard.vue'

defineProps<{
  stats: StatsOverview
  compact?: boolean
}>()
</script>

<template>
  <div class="grid grid-cols-2 gap-2" :class="{ 'grid-cols-3': !compact }">
    <StatCard :value="stats.total_words" label="Total Words" />
    <StatCard :value="stats.current_streak" :label="stats.current_streak === 1 ? 'Day Streak' : 'Days Streak'" />
    <StatCard :value="stats.reviews_today" label="Reviews Today" />
    <StatCard
      :value="stats.accuracy_rate != null ? `${Math.round(stats.accuracy_rate * 100)}%` : '—'"
      label="Accuracy"
    />
    <template v-if="!compact">
      <StatCard :value="stats.words_learning" label="Learning" />
      <StatCard :value="stats.words_known" label="Known" />
      <StatCard :value="stats.due_tomorrow" label="Due Tomorrow" />
    </template>
  </div>
</template>
