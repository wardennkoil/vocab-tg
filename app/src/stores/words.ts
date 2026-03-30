import { ref } from 'vue'
import { defineStore } from 'pinia'
import { useUserStore } from './user'
import {
  getUserWords,
  deleteWord as apiDeleteWord,
  addWord as apiAddWord,
} from '@/api/words'
import type { UserWordResponse } from '@/api/types'

export const useWordsStore = defineStore('words', () => {
  const items = ref<UserWordResponse[]>([])
  const total = ref(0)
  const page = ref(1)
  const perPage = ref(20)
  const statusFilter = ref<string | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchPage(p: number = 1, filter?: string | null) {
    const userStore = useUserStore()
    if (!userStore.telegramId) return
    loading.value = true
    error.value = null
    try {
      if (filter !== undefined) statusFilter.value = filter
      page.value = p
      const result = await getUserWords(userStore.telegramId, {
        status: statusFilter.value ?? undefined,
        page: page.value,
        per_page: perPage.value,
      })
      if (p === 1) {
        items.value = result.items
      } else {
        items.value = [...items.value, ...result.items]
      }
      total.value = result.total
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch words'
    } finally {
      loading.value = false
    }
  }

  async function loadMore() {
    if (items.value.length < total.value) {
      await fetchPage(page.value + 1)
    }
  }

  async function deleteWord(userWordId: number) {
    const userStore = useUserStore()
    if (!userStore.telegramId) return
    try {
      await apiDeleteWord(userStore.telegramId, userWordId)
      items.value = items.value.filter((w) => w.id !== userWordId)
      total.value--
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to delete word'
    }
  }

  async function addWord(word: string) {
    const userStore = useUserStore()
    if (!userStore.telegramId) return
    try {
      const result = await apiAddWord(userStore.telegramId, word)
      items.value.unshift(result)
      total.value++
      return result
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to add word'
      throw e
    }
  }

  function setFilter(filter: string | null) {
    statusFilter.value = filter
    fetchPage(1)
  }

  return {
    items, total, page, perPage, statusFilter, loading, error,
    fetchPage, loadMore, deleteWord, addWord, setFilter,
  }
})
