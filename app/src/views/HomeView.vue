<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useStatsStore } from '@/stores/stats'
import StatsGrid from '@/components/stats/StatsGrid.vue'
import EmptyState from '@/components/layout/EmptyState.vue'

const router = useRouter()
const userStore = useUserStore()
const statsStore = useStatsStore()

onMounted(() => {
  statsStore.fetchOverview()
})
</script>

<template>
  <div class="px-4 py-4">
    <!-- Greeting -->
    <h1 class="mb-4 text-xl font-bold">
      Hello, {{ userStore.user?.first_name || 'there' }}
    </h1>

    <!-- Stats -->
    <template v-if="statsStore.overview && statsStore.overview.total_words > 0">
      <StatsGrid :stats="statsStore.overview" compact class="mb-4" />

      <!-- Action Cards -->
      <div class="flex flex-col gap-3">
        <button
          class="flex items-center justify-between rounded-xl bg-tg-section-bg px-4 py-4 active:opacity-80"
          @click="router.push('/daily')"
        >
          <div class="text-left">
            <span class="block text-base font-semibold">Daily Words</span>
            <span class="text-xs text-tg-hint">Learn new vocabulary</span>
          </div>
          <svg class="h-5 w-5 text-tg-hint" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="9 18 15 12 9 6" />
          </svg>
        </button>

        <button
          class="flex items-center justify-between rounded-xl bg-tg-section-bg px-4 py-4 active:opacity-80"
          @click="router.push('/review')"
        >
          <div class="text-left">
            <span class="block text-base font-semibold">Review</span>
            <span class="text-xs text-tg-hint">
              {{ statsStore.dueCount }} words due
            </span>
          </div>
          <div class="flex items-center gap-2">
            <span
              v-if="statsStore.dueCount > 0"
              class="flex h-6 min-w-6 items-center justify-center rounded-full bg-tg-accent px-1.5 text-xs font-bold text-tg-button-text"
            >
              {{ statsStore.dueCount }}
            </span>
            <svg class="h-5 w-5 text-tg-hint" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="9 18 15 12 9 6" />
            </svg>
          </div>
        </button>

        <button
          class="flex items-center justify-between rounded-xl bg-tg-section-bg px-4 py-4 active:opacity-80"
          @click="router.push('/add')"
        >
          <div class="text-left">
            <span class="block text-base font-semibold">Add Word</span>
            <span class="text-xs text-tg-hint">Search and add custom words</span>
          </div>
          <svg class="h-5 w-5 text-tg-hint" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
        </button>

        <!-- Stats link -->
        <button
          class="text-center text-sm text-tg-accent active:opacity-70"
          @click="router.push('/stats')"
        >
          View full stats
        </button>
      </div>
    </template>

    <!-- Empty State -->
    <template v-else-if="statsStore.overview && statsStore.overview.total_words === 0">
      <EmptyState
        message="You don't have any words yet. Start with your daily words or add custom words!"
        action-label="Get Daily Words"
        @action="router.push('/daily')"
      >
        <template #icon>
          <svg class="h-16 w-16 text-tg-hint" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M4 19.5A2.5 2.5 0 016.5 17H20" />
            <path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z" />
          </svg>
        </template>
      </EmptyState>
    </template>
  </div>
</template>
