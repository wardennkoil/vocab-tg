<script setup lang="ts">
defineProps<{
  title: string
}>()
</script>

<template>
  <div class="mb-6">
    <h3 class="mb-2 px-4 text-xs font-semibold uppercase tracking-wide text-tg-section-header">
      {{ title }}
    </h3>
    <div class="divide-y divide-tg-section-separator rounded-xl bg-tg-section-bg">
      <slot />
    </div>
  </div>
</template>
