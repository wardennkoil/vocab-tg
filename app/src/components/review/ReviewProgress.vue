<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  current: number
  total: number
}>()

const percentage = computed(() =>
  props.total > 0 ? (props.current / props.total) * 100 : 0,
)
</script>

<template>
  <div class="px-4 pt-2">
    <div class="flex items-center justify-between text-xs text-tg-hint">
      <span>{{ current }} / {{ total }}</span>
      <span>{{ Math.round(percentage) }}%</span>
    </div>
    <div class="mt-1 h-1 overflow-hidden rounded-full bg-tg-secondary-bg">
      <div
        class="h-full rounded-full bg-tg-accent transition-all duration-300"
        :style="{ width: `${percentage}%` }"
      />
    </div>
  </div>
</template>
