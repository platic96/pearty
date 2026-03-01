<script setup lang="ts">
import { ref } from 'vue'
import { useCreateAlert } from '@/composables/useAlerts'
import { DEFAULT_MARKETS, INDICATOR_CONDITIONS } from '@/utils/constants'
import type { AlertCreate } from '@/types/alert'

const emit = defineEmits<{ created: [] }>()

const form = ref<AlertCreate>({
  market: 'KRW-BTC',
  indicator: 'RSI',
  condition: 'below',
  threshold: 30,
})

const { mutate: createAlert, isPending } = useCreateAlert()

function handleSubmit() {
  createAlert(form.value, {
    onSuccess: () => {
      form.value = { market: 'KRW-BTC', indicator: 'RSI', condition: 'below', threshold: 30 }
      emit('created')
    },
  })
}

const indicators: Array<'RSI' | 'MACD' | 'BB' | 'PRICE'> = ['RSI', 'MACD', 'BB', 'PRICE']
</script>

<template>
  <form
    class="rounded-lg p-4 space-y-4"
    style="background-color: var(--color-bg-secondary)"
    @submit.prevent="handleSubmit"
  >
    <h3 class="text-sm font-medium">새 알림 생성</h3>

    <div class="grid grid-cols-2 gap-3">
      <!-- Market -->
      <div>
        <label class="text-xs" style="color: var(--color-text-secondary)">마켓</label>
        <select
          v-model="form.market"
          class="mt-1 w-full rounded px-2 py-1.5 text-sm"
          style="background-color: var(--color-bg-tertiary); border: 1px solid var(--color-border); color: var(--color-text-primary)"
        >
          <option v-for="m in DEFAULT_MARKETS" :key="m" :value="`KRW-${m}`">{{ m }}/KRW</option>
        </select>
      </div>

      <!-- Indicator -->
      <div>
        <label class="text-xs" style="color: var(--color-text-secondary)">지표</label>
        <select
          v-model="form.indicator"
          class="mt-1 w-full rounded px-2 py-1.5 text-sm"
          style="background-color: var(--color-bg-tertiary); border: 1px solid var(--color-border); color: var(--color-text-primary)"
        >
          <option v-for="ind in indicators" :key="ind" :value="ind">{{ ind }}</option>
        </select>
      </div>

      <!-- Condition -->
      <div>
        <label class="text-xs" style="color: var(--color-text-secondary)">조건</label>
        <select
          v-model="form.condition"
          class="mt-1 w-full rounded px-2 py-1.5 text-sm"
          style="background-color: var(--color-bg-tertiary); border: 1px solid var(--color-border); color: var(--color-text-primary)"
        >
          <option
            v-for="cond in (INDICATOR_CONDITIONS[form.indicator] || INDICATOR_CONDITIONS.RSI)"
            :key="cond.value"
            :value="cond.value"
          >
            {{ cond.label }}
          </option>
        </select>
      </div>

      <!-- Threshold -->
      <div>
        <label class="text-xs" style="color: var(--color-text-secondary)">기준값</label>
        <input
          v-model.number="form.threshold"
          type="number"
          step="any"
          class="mt-1 w-full rounded px-2 py-1.5 text-sm"
          style="background-color: var(--color-bg-tertiary); border: 1px solid var(--color-border); color: var(--color-text-primary)"
        />
      </div>
    </div>

    <button
      type="submit"
      :disabled="isPending"
      class="w-full py-2 rounded-lg text-sm font-medium text-white bg-indigo-500 hover:bg-indigo-600 disabled:opacity-50 transition-colors"
    >
      {{ isPending ? '생성 중...' : '알림 생성' }}
    </button>
  </form>
</template>
