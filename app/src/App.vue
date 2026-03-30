<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import TabBar from '@/components/layout/TabBar.vue'
import LoadingSpinner from '@/components/layout/LoadingSpinner.vue'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const userStore = useUserStore()

const showTabBar = computed(() => {
  return route.name !== 'review'
})

onMounted(() => {
  userStore.init()
})
</script>

<template>
  <div class="flex min-h-screen flex-col bg-tg-bg text-tg-text">
    <template v-if="userStore.loading">
      <LoadingSpinner />
    </template>
    <template v-else>
      <main class="flex-1" :class="{ 'pb-20': showTabBar }">
        <RouterView />
      </main>
      <TabBar v-if="showTabBar" />
    </template>
  </div>
</template>
