<script setup lang="ts">
defineProps<{
  value: string | number
  label: string
}>()
</script>

<template>
  <div class="rounded-xl bg-tg-section-bg p-3 text-center">
    <div class="text-2xl font-bold text-tg-text">{{ value }}</div>
    <div class="mt-0.5 text-xs text-tg-hint">{{ label }}</div>
  </div>
</template>
