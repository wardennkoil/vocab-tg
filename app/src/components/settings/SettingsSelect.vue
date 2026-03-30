<script setup lang="ts">
defineProps<{
  label: string
  options: { value: string | number; label: string }[]
  modelValue: string | number
}>()

defineEmits<{
  'update:modelValue': [value: string | number]
}>()
</script>

<template>
  <div class="px-4 py-3">
    <span class="mb-2 block text-sm">{{ label }}</span>
    <div class="flex flex-wrap gap-1.5">
      <button
        v-for="opt in options"
        :key="opt.value"
        class="rounded-lg px-3 py-1.5 text-xs font-medium transition-colors"
        :class="
          modelValue === opt.value
            ? 'bg-tg-accent text-tg-button-text'
            : 'bg-tg-secondary-bg text-tg-text'
        "
        @click="$emit('update:modelValue', opt.value)"
      >
        {{ opt.label }}
      </button>
    </div>
  </div>
</template>
