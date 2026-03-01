<script setup lang="ts">
defineProps<{
  message: string
}>()
</script>

<template>
  <div class="flex flex-col items-center justify-center p-12 text-center" style="color: var(--color-text-secondary)">
    <p class="text-sm">{{ message }}</p>
  </div>
</template>
