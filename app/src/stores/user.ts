import { ref } from 'vue'
import { defineStore } from 'pinia'
import { getTelegramUserId, getTelegramUser } from '@/telegram/init'
import { registerUser, updateSettings as apiUpdateSettings } from '@/api/users'
import type { UserResponse, UserSettingsUpdate } from '@/api/types'

export const useUserStore = defineStore('user', () => {
  const user = ref<UserResponse | null>(null)
  const telegramId = ref<number | null>(null)
  const loading = ref(true)
  const error = ref<string | null>(null)

  async function init() {
    loading.value = true
    error.value = null

    const tgId = getTelegramUserId()
    if (!tgId) {
      loading.value = false
      error.value = 'Could not get Telegram user ID'
      return
    }

    telegramId.value = tgId
    const tgUser = getTelegramUser()

    try {
      user.value = await registerUser({
        telegram_id: tgId,
        username: tgUser?.username ?? null,
        first_name: tgUser?.first_name ?? null,
        language_code: tgUser?.language_code ?? null,
      })
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to register user'
    } finally {
      loading.value = false
    }
  }

  async function updateSettings(settings: UserSettingsUpdate) {
    if (!telegramId.value) return
    try {
      user.value = await apiUpdateSettings(telegramId.value, settings)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to update settings'
    }
  }

  return { user, telegramId, loading, error, init, updateSettings }
})
