<script setup lang="ts">
import { onMounted } from 'vue'
import { useStatsStore } from '@/stores/stats'
import { useTelegramBackButton } from '@/composables/useTelegramBackButton'
import PageHeader from '@/components/layout/PageHeader.vue'
import StatsGrid from '@/components/stats/StatsGrid.vue'
import ActivityChart from '@/components/stats/ActivityChart.vue'

useTelegramBackButton()
const statsStore = useStatsStore()

onMounted(() => {
  statsStore.fetchOverview()
  statsStore.fetchHistory(30)
})
</script>

<template>
  <div>
    <PageHeader title="Statistics" />
    <div class="px-4">
      <StatsGrid v-if="statsStore.overview" :stats="statsStore.overview" class="mb-4" />
      <ActivityChart v-if="statsStore.history.length > 0" :days="statsStore.history" />
    </div>
  </div>
</template>
