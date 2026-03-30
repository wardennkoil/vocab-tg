import { request } from './client'
import type { UserRegister, UserResponse, UserSettingsUpdate } from './types'

export function registerUser(data: UserRegister): Promise<UserResponse> {
  return request('/users/register', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export function getUser(telegramId: number): Promise<UserResponse> {
  return request(`/users/${telegramId}`)
}

export function updateSettings(
  telegramId: number,
  data: UserSettingsUpdate,
): Promise<UserResponse> {
  return request(`/users/${telegramId}/settings`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}
