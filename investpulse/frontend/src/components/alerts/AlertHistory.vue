<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAlertHistory } from '@/composables/useAlertHistory'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import EmptyState from '@/components/common/EmptyState.vue'

const page = ref(1)
const filterMarket = ref<string | undefined>()
const filterIndicator = ref<string | undefined>()

const params = computed(() => ({
  page: page.value,
  size: 20,
  market: filterMarket.value || undefined,
  indicator: filterIndicator.value || undefined,
}))

const { data: historyPage, isLoading } = useAlertHistory(params)

const statusLabels: Record<string, { text: string; class: string }> = {
  triggered: { text: '발동', class: 'bg-amber-500/20 text-amber-400' },
  sent: { text: '전송 완료', class: 'bg-green-500/20 text-green-400' },
  failed: { text: '전송 실패', class: 'bg-red-500/20 text-red-400' },
}

const conditionLabels: Record<string, string> = {
  above: '이상',
  below: '이하',
  cross_up: '골든크로스',
  cross_down: '데드크로스',
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleString('ko-KR', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>

<template>
  <div class="space-y-4">
    <!-- 필터 -->
    <div class="flex gap-2">
      <input
        v-model="filterMarket"
        type="text"
        placeholder="마켓 필터 (예: KRW-BTC)"
        class="rounded px-2 py-1 text-xs flex-1"
        style="background-color: var(--color-bg-tertiary); border: 1px solid var(--color-border); color: var(--color-text-primary)"
      />
      <select
        v-model="filterIndicator"
        class="rounded px-2 py-1 text-xs"
        style="background-color: var(--color-bg-tertiary); border: 1px solid var(--color-border); color: var(--color-text-primary)"
      >
        <option :value="undefined">전체 지표</option>
        <option value="RSI">RSI</option>
        <option value="MACD">MACD</option>
        <option value="BB">BB</option>
        <option value="PRICE">PRICE</option>
        <option value="CHANGE_RATE">CHANGE_RATE</option>
      </select>
    </div>

    <LoadingSpinner v-if="isLoading" />
    <EmptyState v-else-if="!historyPage?.items.length" message="알림 히스토리가 없습니다." />

    <div v-else class="space-y-2">
      <!-- 타임라인 -->
      <div
        v-for="item in historyPage.items"
        :key="item.id"
        class="flex gap-3 p-3 rounded-lg"
        style="background-color: var(--color-bg-secondary)"
      >
        <!-- 타임라인 dot -->
        <div class="flex flex-col items-center shrink-0">
          <div
            class="w-2.5 h-2.5 rounded-full mt-1"
            :class="item.status === 'sent' ? 'bg-green-400' : item.status === 'failed' ? 'bg-red-400' : 'bg-amber-400'"
          />
          <div class="w-px flex-1 mt-1" style="background-color: var(--color-border)" />
        </div>

        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2 flex-wrap">
            <span class="text-xs font-medium">{{ item.market }}</span>
            <span class="text-xs px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-400">
              {{ item.indicator }}
            </span>
            <span
              class="text-xs px-1.5 py-0.5 rounded"
              :class="statusLabels[item.status]?.class ?? 'bg-gray-500/20 text-gray-400'"
            >
              {{ statusLabels[item.status]?.text ?? item.status }}
            </span>
            <span class="text-xs ml-auto" style="color: var(--color-text-secondary)">
              {{ formatDate(item.triggered_at) }}
            </span>
          </div>

          <p class="text-xs mt-1" style="color: var(--color-text-secondary)">
            {{ item.indicator }} {{ conditionLabels[item.condition ?? ''] || item.condition }}
            {{ item.threshold }}
            <span v-if="item.indicator_value != null">
              · 현재값: {{ item.indicator_value.toLocaleString('ko-KR', { maximumFractionDigits: 2 }) }}
            </span>
          </p>

          <p
            v-if="item.message"
            class="text-xs mt-1 text-red-400/80"
          >
            {{ item.message }}
          </p>
        </div>
      </div>

      <!-- 페이지네이션 -->
      <div class="flex items-center justify-between pt-2">
        <span class="text-xs" style="color: var(--color-text-secondary)">
          총 {{ historyPage.total }}건
        </span>
        <div class="flex gap-1">
          <button
            :disabled="page <= 1"
            class="text-xs px-2 py-1 rounded disabled:opacity-30 hover:bg-indigo-500/20 text-indigo-400 transition-colors"
            @click="page--"
          >
            이전
          </button>
          <span class="text-xs px-2 py-1" style="color: var(--color-text-secondary)">
            {{ historyPage.page }} / {{ historyPage.pages }}
          </span>
          <button
            :disabled="page >= historyPage.pages"
            class="text-xs px-2 py-1 rounded disabled:opacity-30 hover:bg-indigo-500/20 text-indigo-400 transition-colors"
            @click="page++"
          >
            다음
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
