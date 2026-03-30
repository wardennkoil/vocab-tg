<script setup lang="ts">
import { computed } from 'vue'
import type { DayStats } from '@/api/types'

const props = defineProps<{
  days: DayStats[]
}>()

const chartWidth = 300
const chartHeight = 120
const barGap = 2

const maxCount = computed(() =>
  Math.max(1, ...props.days.map((d) => d.review_count)),
)

const barWidth = computed(() =>
  Math.max(2, (chartWidth - barGap * props.days.length) / props.days.length),
)

const bars = computed(() =>
  props.days.map((d, i) => {
    const height = (d.review_count / maxCount.value) * (chartHeight - 20)
    return {
      x: i * (barWidth.value + barGap),
      y: chartHeight - 20 - height,
      width: barWidth.value,
      height: Math.max(1, height),
      count: d.review_count,
      date: d.date,
    }
  }),
)

function formatDate(dateStr: string) {
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}/${d.getDate()}`
}
</script>

<template>
  <div class="rounded-xl bg-tg-section-bg p-4">
    <h3 class="mb-3 text-sm font-medium text-tg-section-header">Activity (last {{ days.length }} days)</h3>
    <svg
      :viewBox="`0 0 ${chartWidth} ${chartHeight}`"
      class="w-full"
      preserveAspectRatio="xMidYMid meet"
    >
      <rect
        v-for="(bar, i) in bars"
        :key="i"
        :x="bar.x"
        :y="bar.y"
        :width="bar.width"
        :height="bar.height"
        rx="1"
        class="fill-tg-accent"
        opacity="0.8"
      >
        <title>{{ formatDate(bar.date) }}: {{ bar.count }} reviews</title>
      </rect>
      <!-- X axis labels every 7 days -->
      <text
        v-for="(bar, i) in bars.filter((_, i) => i % 7 === 0)"
        :key="'label-' + i"
        :x="bar.x + bar.width / 2"
        :y="chartHeight - 2"
        text-anchor="middle"
        class="fill-tg-hint text-[8px]"
      >
        {{ formatDate(bar.date) }}
      </text>
    </svg>
  </div>
</template>
