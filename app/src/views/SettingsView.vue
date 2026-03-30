<script setup lang="ts">
import { computed } from 'vue'
import { useUserStore } from '@/stores/user'
import PageHeader from '@/components/layout/PageHeader.vue'
import SettingsGroup from '@/components/settings/SettingsGroup.vue'
import SettingsToggle from '@/components/settings/SettingsToggle.vue'
import SettingsSelect from '@/components/settings/SettingsSelect.vue'

const userStore = useUserStore()

const difficultyOptions = [
  { value: 'B1-B2', label: 'B1-B2' },
  { value: 'B2-C1', label: 'B2-C1' },
  { value: 'C1-C2', label: 'C1-C2' },
]

const wordCountOptions = [
  { value: 3, label: '3' },
  { value: 5, label: '5' },
  { value: 7, label: '7' },
  { value: 10, label: '10' },
]

const hourOptions = Array.from({ length: 17 }, (_, i) => ({
  value: i + 6,
  label: `${i + 6}:00`,
}))

const timezones = computed(() => {
  try {
    return Intl.supportedValuesOf('timeZone').map((tz) => ({
      value: tz,
      label: tz.replace(/_/g, ' '),
    }))
  } catch {
    return [{ value: 'UTC', label: 'UTC' }]
  }
})

function updateDifficulty(value: string | number) {
  userStore.updateSettings({ difficulty_level: String(value) })
}

function updateWordCount(value: string | number) {
  userStore.updateSettings({ daily_word_count: Number(value) })
}

function updateSkipTriage(value: boolean) {
  userStore.updateSettings({ skip_triage: value })
}

function updatePushHour(value: string | number) {
  userStore.updateSettings({ daily_push_hour: Number(value) })
}

function updateTimezone(event: Event) {
  const target = event.target as HTMLSelectElement
  userStore.updateSettings({ timezone: target.value })
}
</script>

<template>
  <div>
    <PageHeader title="Settings" />

    <div v-if="userStore.user" class="py-2">
      <SettingsGroup title="Learning">
        <SettingsSelect
          label="Difficulty Level"
          :options="difficultyOptions"
          :model-value="userStore.user.difficulty_level"
          @update:model-value="updateDifficulty"
        />
        <SettingsSelect
          label="Daily Word Count"
          :options="wordCountOptions"
          :model-value="userStore.user.daily_word_count"
          @update:model-value="updateWordCount"
        />
        <SettingsToggle
          label="Skip Triage"
          description="Auto-select daily words without manual picking"
          :model-value="userStore.user.skip_triage"
          @update:model-value="updateSkipTriage"
        />
      </SettingsGroup>

      <SettingsGroup title="Notifications">
        <SettingsSelect
          label="Push Reminder Hour"
          :options="hourOptions"
          :model-value="userStore.user.daily_push_hour"
          @update:model-value="updatePushHour"
        />
        <div class="px-4 py-3">
          <span class="mb-2 block text-sm">Timezone</span>
          <select
            :value="userStore.user.timezone"
            class="w-full rounded-lg bg-tg-secondary-bg px-3 py-2 text-sm"
            @change="updateTimezone"
          >
            <option
              v-for="tz in timezones"
              :key="tz.value"
              :value="tz.value"
            >
              {{ tz.label }}
            </option>
          </select>
        </div>
      </SettingsGroup>
    </div>
  </div>
</template>
