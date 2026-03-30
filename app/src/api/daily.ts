import { request } from './client'
import type {
  TriageCandidatesResponse,
  TriageSubmitPayload,
  WordCard,
  DailyWordsResponse,
} from './types'

export function getTriageCandidates(
  telegramId: number,
): Promise<TriageCandidatesResponse> {
  return request(`/users/${telegramId}/daily/triage`, { method: 'POST' })
}

export function submitTriage(
  telegramId: number,
  data: TriageSubmitPayload,
): Promise<WordCard[]> {
  return request(`/users/${telegramId}/daily/triage/submit`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export function autoSelectDaily(
  telegramId: number,
): Promise<WordCard[]> {
  return request(`/users/${telegramId}/daily/auto-select`, { method: 'POST' })
}

export function getTodayWords(
  telegramId: number,
): Promise<DailyWordsResponse> {
  return request(`/users/${telegramId}/daily/today`)
}
