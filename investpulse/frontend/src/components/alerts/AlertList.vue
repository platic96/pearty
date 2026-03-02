<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAlerts, useDeleteAlert, useUpdateAlert, useDuplicateAlert, useBulkAlertAction } from '@/composables/useAlerts'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import type { Alert } from '@/types/alert'

const emit = defineEmits<{
  edit: [alert: Alert]
}>()

const { data: alerts, isLoading } = useAlerts()
const { mutate: deleteAlert } = useDeleteAlert()
const { mutate: updateAlert } = useUpdateAlert()
const { mutate: duplicateAlert } = useDuplicateAlert()
const { mutate: bulkAction } = useBulkAlertAction()

// 필터
const filterMarket = ref<string>('')
const filterIndicator = ref<string>('')
const filterActive = ref<string>('')

const filteredAlerts = computed(() => {
  if (!alerts.value) return []
  let result = alerts.value
  if (filterMarket.value) {
    result = result.filter(a => a.market === filterMarket.value)
  }
  if (filterIndicator.value) {
    result = result.filter(a => a.indicator === filterIndicator.value)
  }
  if (filterActive.value !== '') {
    const isActive = filterActive.value === 'true'
    result = result.filter(a => a.is_active === isActive)
  }
  return result
})

// 다중 선택
const selectedIds = ref<Set<number>>(new Set())

const allSelected = computed(() =>
  filteredAlerts.value.length > 0 && filteredAlerts.value.every(a => selectedIds.value.has(a.id))
)

function toggleSelectAll() {
  if (allSelected.value) {
    selectedIds.value.clear()
  } else {
    selectedIds.value = new Set(filteredAlerts.value.map(a => a.id))
  }
}

function toggleSelect(id: number) {
  if (selectedIds.value.has(id)) {
    selectedIds.value.delete(id)
  } else {
    selectedIds.value.add(id)
  }
}

function handleBulk(action: 'activate' | 'deactivate' | 'delete') {
  bulkAction(
    { alert_ids: [...selectedIds.value], action },
    { onSuccess: () => selectedIds.value.clear() },
  )
}

function toggleActive(id: number, currentActive: boolean) {
  updateAlert({ id, data: { is_active: !currentActive } })
}

// 유니크 마켓/지표 목록 (필터용)
const uniqueMarkets = computed(() =>
  [...new Set(alerts.value?.map(a => a.market) ?? [])].sort()
)
const uniqueIndicators = computed(() =>
  [...new Set(alerts.value?.map(a => a.indicator) ?? [])].sort()
)

const conditionLabels: Record<string, string> = {
  above: '이상',
  below: '이하',
  cross_up: '골든크로스',
  cross_down: '데드크로스',
}
</script>

<template>
  <div class="space-y-3">
    <!-- 필터 바 -->
    <div class="flex flex-wrap gap-2 items-center">
      <select
        v-model="filterMarket"
        class="rounded px-2 py-1 text-xs"
        style="background-color: var(--color-bg-tertiary); border: 1px solid var(--color-border); color: var(--color-text-primary)"
      >
        <option value="">전체 마켓</option>
        <option v-for="m in uniqueMarkets" :key="m" :value="m">{{ m }}</option>
      </select>

      <select
        v-model="filterIndicator"
        class="rounded px-2 py-1 text-xs"
        style="background-color: var(--color-bg-tertiary); border: 1px solid var(--color-border); color: var(--color-text-primary)"
      >
        <option value="">전체 지표</option>
        <option v-for="i in uniqueIndicators" :key="i" :value="i">{{ i }}</option>
      </select>

      <select
        v-model="filterActive"
        class="rounded px-2 py-1 text-xs"
        style="background-color: var(--color-bg-tertiary); border: 1px solid var(--color-border); color: var(--color-text-primary)"
      >
        <option value="">전체 상태</option>
        <option value="true">활성</option>
        <option value="false">비활성</option>
      </select>

      <span class="text-xs ml-auto" style="color: var(--color-text-secondary)">
        {{ filteredAlerts.length }}개
      </span>
    </div>

    <!-- Bulk 액션 바 -->
    <div
      v-if="selectedIds.size > 0"
      class="flex items-center gap-2 p-2 rounded-lg bg-indigo-500/10 border border-indigo-500/30"
    >
      <span class="text-xs text-indigo-400">{{ selectedIds.size }}개 선택</span>
      <button
        class="text-xs px-2 py-0.5 rounded bg-green-500/20 text-green-400 hover:bg-green-500/30"
        @click="handleBulk('activate')"
      >활성화</button>
      <button
        class="text-xs px-2 py-0.5 rounded bg-gray-500/20 text-gray-400 hover:bg-gray-500/30"
        @click="handleBulk('deactivate')"
      >비활성화</button>
      <button
        class="text-xs px-2 py-0.5 rounded bg-red-500/20 text-red-400 hover:bg-red-500/30"
        @click="handleBulk('delete')"
      >삭제</button>
    </div>

    <LoadingSpinner v-if="isLoading" />
    <EmptyState v-else-if="!filteredAlerts.length" message="등록된 알림이 없습니다." />
    <div v-else class="space-y-2">
      <!-- 전체 선택 -->
      <div class="flex items-center gap-2 px-2">
        <input
          type="checkbox"
          :checked="allSelected"
          class="rounded"
          @change="toggleSelectAll"
        />
        <span class="text-xs" style="color: var(--color-text-secondary)">전체 선택</span>
      </div>

      <div
        v-for="alert in filteredAlerts"
        :key="alert.id"
        class="flex items-center gap-3 p-4 rounded-lg"
        style="background-color: var(--color-bg-secondary)"
      >
        <!-- Checkbox -->
        <input
          type="checkbox"
          :checked="selectedIds.has(alert.id)"
          class="rounded shrink-0"
          @change="toggleSelect(alert.id)"
        />

        <!-- Info -->
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2 flex-wrap">
            <span class="font-medium text-sm">{{ alert.market }}</span>
            <span class="text-xs px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-400">
              {{ alert.indicator }}
            </span>
            <span
              v-if="alert.trigger_count > 0"
              class="text-xs px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-400"
            >
              {{ alert.trigger_count }}회 발동
            </span>
          </div>
          <p class="text-xs mt-1" style="color: var(--color-text-secondary)">
            {{ alert.indicator }} {{ conditionLabels[alert.condition] || alert.condition }} {{ alert.threshold }}
            <span v-if="alert.cooldown_minutes > 0"> · 쿨다운 {{ alert.cooldown_minutes }}분</span>
          </p>
          <p v-if="alert.last_triggered_at" class="text-xs mt-0.5" style="color: var(--color-text-secondary)">
            마지막 발동: {{ new Date(alert.last_triggered_at).toLocaleString('ko-KR') }}
          </p>
        </div>

        <!-- Actions -->
        <div class="flex items-center gap-1 shrink-0">
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

          <!-- Edit -->
          <button
            class="text-xs px-2 py-1 rounded hover:bg-indigo-500/20 text-indigo-400 transition-colors"
            @click="emit('edit', alert)"
          >
            수정
          </button>

          <!-- Duplicate -->
          <button
            class="text-xs px-2 py-1 rounded hover:bg-blue-500/20 text-blue-400 transition-colors"
            @click="duplicateAlert(alert.id)"
          >
            복제
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
  </div>
</template>
