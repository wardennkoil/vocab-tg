import { init, miniApp, initData, themeParams } from '@tma.js/sdk-vue'

export function initTelegramApp(): void {
  try {
    init()

    miniApp.mount()
    miniApp.ready()

    themeParams.mount()
    themeParams.bindCssVars()

    initData.restore()
  } catch {
    // SDK may fail outside Telegram environment (dev mode)
    console.warn('Telegram SDK init failed — running outside Telegram?')
  }
}

export function getTelegramUserId(): number | null {
  try {
    return initData.user()?.id ?? null
  } catch {
    return null
  }
}

export function getTelegramUser() {
  try {
    return initData.user() ?? null
  } catch {
    return null
  }
}
