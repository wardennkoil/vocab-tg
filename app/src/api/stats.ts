import { request } from './client'
import type { StatsOverview, StatsHistory } from './types'

export function getStats(telegramId: number): Promise<StatsOverview> {
  return request(`/users/${telegramId}/stats`)
}

export function getStatsHistory(
  telegramId: number,
  days: number = 30,
): Promise<StatsHistory> {
  return request(`/users/${telegramId}/stats/history?days=${days}`)
}
