<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  status: string
}>()

const badge = computed(() => {
  switch (props.status) {
    case 'learning':
      return { label: 'L', class: 'bg-blue-100 text-blue-700' }
    case 'reviewing':
      return { label: 'R', class: 'bg-amber-100 text-amber-700' }
    case 'known':
      return { label: 'K', class: 'bg-green-100 text-green-700' }
    case 'custom':
      return { label: 'C', class: 'bg-purple-100 text-purple-700' }
    default:
      return { label: props.status[0]?.toUpperCase() ?? '?', class: 'bg-tg-secondary-bg text-tg-hint' }
  }
})
</script>

<template>
  <span
    class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-[10px] font-bold"
    :class="badge.class"
  >
    {{ badge.label }}
  </span>
</template>
