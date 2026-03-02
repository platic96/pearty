<script setup lang="ts">
import { ref } from 'vue'
import AlertForm from '@/components/alerts/AlertForm.vue'
import AlertList from '@/components/alerts/AlertList.vue'
import AlertHistory from '@/components/alerts/AlertHistory.vue'
import type { Alert } from '@/types/alert'

const activeTab = ref<'manage' | 'history'>('manage')
const editingAlert = ref<Alert | null>(null)

function handleEdit(alert: Alert) {
  editingAlert.value = alert
}

function handleFormDone() {
  editingAlert.value = null
}

const tabs = [
  { key: 'manage' as const, label: '알림 관리' },
  { key: 'history' as const, label: '발동 히스토리' },
]
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h2 class="text-2xl font-bold">Alerts</h2>

      <!-- 탭 -->
      <div class="flex gap-1 rounded-lg p-1" style="background-color: var(--color-bg-secondary)">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          class="px-3 py-1.5 rounded-md text-sm transition-colors"
          :class="activeTab === tab.key
            ? 'bg-indigo-500 text-white'
            : 'text-gray-400 hover:text-white'"
          @click="activeTab = tab.key"
        >
          {{ tab.label }}
        </button>
      </div>
    </div>

    <!-- 알림 관리 탭 -->
    <div v-if="activeTab === 'manage'" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-1">
        <AlertForm
          :edit-alert="editingAlert"
          @created="handleFormDone"
          @updated="handleFormDone"
          @cancel="handleFormDone"
        />
      </div>
      <div class="lg:col-span-2">
        <AlertList @edit="handleEdit" />
      </div>
    </div>

    <!-- 히스토리 탭 -->
    <div v-else-if="activeTab === 'history'">
      <AlertHistory />
    </div>
  </div>
</template>
