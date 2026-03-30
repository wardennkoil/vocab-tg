import { ref } from 'vue'
import { defineStore } from 'pinia'
import { useUserStore } from './user'
import { getStats, getStatsHistory } from '@/api/stats'
import { getDueCount } from '@/api/reviews'
import type { StatsOverview, DayStats } from '@/api/types'

export const useStatsStore = defineStore('stats', () => {
  const overview = ref<StatsOverview | null>(null)
  const history = ref<DayStats[]>([])
  const dueCount = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchOverview() {
    const userStore = useUserStore()
    if (!userStore.telegramId) return
    loading.value = true
    error.value = null
    try {
      const [stats, due] = await Promise.all([
        getStats(userStore.telegramId),
        getDueCount(userStore.telegramId),
      ])
      overview.value = stats
      dueCount.value = due.due_count
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch stats'
    } finally {
      loading.value = false
    }
  }

  async function fetchHistory(days: number = 30) {
    const userStore = useUserStore()
    if (!userStore.telegramId) return
    try {
      const result = await getStatsHistory(userStore.telegramId, days)
      history.value = result.days
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch history'
    }
  }

  return { overview, history, dueCount, loading, error, fetchOverview, fetchHistory }
})
