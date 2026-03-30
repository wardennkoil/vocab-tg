<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
  url: string
}>()

const playing = ref(false)

function play() {
  const audio = new Audio(props.url)
  playing.value = true
  audio.addEventListener('ended', () => { playing.value = false })
  audio.addEventListener('error', () => { playing.value = false })
  audio.play()
}
</script>

<template>
  <button
    class="flex h-8 w-8 items-center justify-center rounded-full bg-tg-secondary-bg active:opacity-70"
    :class="{ 'animate-pulse': playing }"
    @click.stop="play"
  >
    <svg class="h-4 w-4 text-tg-accent" viewBox="0 0 24 24" fill="currentColor">
      <path d="M8 5v14l11-7z" />
    </svg>
  </button>
</template>
