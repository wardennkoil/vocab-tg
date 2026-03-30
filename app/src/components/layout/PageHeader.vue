<script setup lang="ts">
defineProps<{
  title: string
  showBack?: boolean
}>()
</script>

<template>
  <header class="sticky top-0 z-40 flex items-center gap-3 bg-tg-bg px-4 py-3">
    <h1 class="text-lg font-semibold">{{ title }}</h1>
  </header>
</template>
