<script setup lang="ts">
defineProps<{
  label: string
  description?: string
  modelValue: boolean
}>()

defineEmits<{
  'update:modelValue': [value: boolean]
}>()
</script>

<template>
  <div class="flex items-center justify-between px-4 py-3">
    <div>
      <span class="text-sm">{{ label }}</span>
      <p v-if="description" class="text-xs text-tg-hint">{{ description }}</p>
    </div>
    <button
      class="relative h-7 w-12 rounded-full transition-colors"
      :class="modelValue ? 'bg-tg-accent' : 'bg-tg-secondary-bg'"
      @click="$emit('update:modelValue', !modelValue)"
    >
      <span
        class="absolute top-0.5 left-0.5 h-6 w-6 rounded-full bg-white shadow transition-transform"
        :class="{ 'translate-x-5': modelValue }"
      />
    </button>
  </div>
</template>
