import { request } from './client'
import type {
  ReviewBatchResult,
  ReviewBatchSubmitPayload,
  ReviewResult,
  ReviewSession,
  ReviewSubmitPayload,
} from './types'

export function getDueCount(
  telegramId: number,
): Promise<{ due_count: number }> {
  return request(`/users/${telegramId}/reviews/due`)
}

export function createReviewSession(
  telegramId: number,
): Promise<ReviewSession> {
  return request(`/users/${telegramId}/reviews/session`, { method: 'POST' })
}

export function submitReview(
  telegramId: number,
  data: ReviewSubmitPayload,
): Promise<ReviewResult> {
  return request(`/users/${telegramId}/reviews/submit`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export function submitReviewBatch(
  telegramId: number,
  data: ReviewBatchSubmitPayload,
): Promise<ReviewBatchResult> {
  return request(`/users/${telegramId}/reviews/submit-batch`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
}
