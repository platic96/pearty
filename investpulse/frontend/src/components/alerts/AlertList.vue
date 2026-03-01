<script setup lang="ts">
import { useAlerts, useDeleteAlert, useUpdateAlert } from '@/composables/useAlerts'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import EmptyState from '@/components/common/EmptyState.vue'

const { data: alerts, isLoading } = useAlerts()
const { mutate: deleteAlert } = useDeleteAlert()
const { mutate: updateAlert } = useUpdateAlert()

function toggleActive(id: number, currentActive: boolean) {
  updateAlert({ id, data: { is_active: !currentActive } })
}

const conditionLabels: Record<string, string> = {
  above: '이상',
  below: '이하',
  cross_up: '골든크로스',
  cross_down: '데드크로스',
}
</script>

<template>
  <LoadingSpinner v-if="isLoading" />
  <EmptyState v-else-if="!alerts?.length" message="등록된 알림이 없습니다." />
  <div v-else class="space-y-2">
    <div
      v-for="alert in alerts"
      :key="alert.id"
      class="flex items-center justify-between p-4 rounded-lg"
      style="background-color: var(--color-bg-secondary)"
    >
      <div class="flex-1">
        <div class="flex items-center gap-2">
          <span class="font-medium text-sm">{{ alert.market }}</span>
          <span class="text-xs px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-400">
            {{ alert.indicator }}
          </span>
        </div>
        <p class="text-xs mt-1" style="color: var(--color-text-secondary)">
          {{ alert.indicator }} {{ conditionLabels[alert.condition] || alert.condition }} {{ alert.threshold }}
        </p>
        <p v-if="alert.last_triggered_at" class="text-xs mt-0.5" style="color: var(--color-text-secondary)">
          마지막 발동: {{ new Date(alert.last_triggered_at).toLocaleString('ko-KR') }}
        </p>
      </div>

      <div class="flex items-center gap-2">
        <!-- Toggle active -->
        <button
          class="relative w-10 h-5 rounded-full transition-colors"
          :class="alert.is_active ? 'bg-indigo-500' : 'bg-gray-600'"
          @click="toggleActive(alert.id, alert.is_active)"
        >
          <span
            class="absolute top-0.5 left-0.5 w-4 h-4 rounded-full bg-white transition-transform"
            :class="{ 'translate-x-5': alert.is_active }"
          />
        </button>

        <!-- Delete -->
        <button
          class="text-xs px-2 py-1 rounded hover:bg-red-500/20 text-red-400 transition-colors"
          @click="deleteAlert(alert.id)"
        >
          삭제
        </button>
      </div>
    </div>
  </div>
</template>
