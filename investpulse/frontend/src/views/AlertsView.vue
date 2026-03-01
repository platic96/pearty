<script setup lang="ts">
import AlertForm from '@/components/alerts/AlertForm.vue'
import AlertList from '@/components/alerts/AlertList.vue'
</script>

<template>
  <div class="space-y-6">
    <h2 class="text-2xl font-bold">Alerts</h2>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Alert Form -->
      <div class="lg:col-span-1">
        <AlertForm />
      </div>

      <!-- Alert List -->
      <div class="lg:col-span-2">
        <AlertList />
      </div>
    </div>
  </div>
</template>
