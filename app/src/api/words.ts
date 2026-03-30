import { request } from './client'
import type {
  WordCard,
  WordSuggestion,
  UserWordResponse,
  PaginatedUserWords,
} from './types'

export function searchWords(query: string): Promise<WordSuggestion[]> {
  return request(`/words/search?q=${encodeURIComponent(query)}`)
}

export function getWordCard(word: string): Promise<WordCard> {
  return request(`/words/${encodeURIComponent(word)}`)
}

export function addWord(
  telegramId: number,
  word: string,
): Promise<UserWordResponse> {
  return request(`/users/${telegramId}/words`, {
    method: 'POST',
    body: JSON.stringify({ word }),
  })
}

export function getUserWords(
  telegramId: number,
  params: { status?: string; page?: number; per_page?: number } = {},
): Promise<PaginatedUserWords> {
  const searchParams = new URLSearchParams()
  if (params.status) searchParams.set('status', params.status)
  if (params.page) searchParams.set('page', String(params.page))
  if (params.per_page) searchParams.set('per_page', String(params.per_page))
  const qs = searchParams.toString()
  return request(`/users/${telegramId}/words${qs ? `?${qs}` : ''}`)
}

export function deleteWord(
  telegramId: number,
  userWordId: number,
): Promise<{ status: string }> {
  return request(`/users/${telegramId}/words/${userWordId}`, {
    method: 'DELETE',
  })
}
