import { onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { backButton } from '@tma.js/sdk-vue'

export function useTelegramBackButton(): void {
  const router = useRouter()

  const handleBack = () => {
    router.back()
  }

  onMounted(() => {
    if (backButton.mount.isAvailable()) {
      backButton.mount()
      backButton.show()
      backButton.onClick(handleBack)
    }
  })

  onUnmounted(() => {
    if (backButton.hide.isAvailable()) {
      backButton.hide()
    }
    backButton.offClick(handleBack)
  })
}
