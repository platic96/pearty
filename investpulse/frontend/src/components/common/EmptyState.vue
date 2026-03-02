<script setup lang="ts">
defineProps<{
  message?: string
  title?: string
  description?: string
}>()
</script>

<template>
  <div class="flex flex-col items-center justify-center p-12 text-center" style="color: var(--color-text-secondary)">
    <p v-if="title" class="text-sm font-medium mb-1" style="color: var(--color-text-primary)">{{ title }}</p>
    <p class="text-sm">{{ description || message }}</p>
  </div>
</template>
