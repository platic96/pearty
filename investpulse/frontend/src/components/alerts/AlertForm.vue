<script setup lang="ts">
import { ref, watch } from 'vue'
import { useCreateAlert, useUpdateAlert } from '@/composables/useAlerts'
import { DEFAULT_MARKETS, INDICATOR_CONDITIONS } from '@/utils/constants'
import type { Alert, AlertCreate, IndicatorType } from '@/types/alert'

const props = defineProps<{
  editAlert?: Alert | null
}>()

const emit = defineEmits<{
  created: []
  updated: []
  cancel: []
}>()

const isEditMode = ref(false)
const editingId = ref<number | null>(null)

const defaultForm: AlertCreate = {
  market: 'KRW-BTC',
  indicator: 'RSI',
  condition: 'below',
  threshold: 30,
  cooldown_minutes: 30,
}

const form = ref<AlertCreate>({ ...defaultForm })

const { mutate: create, isPending: isCreating } = useCreateAlert()
const { mutate: update, isPending: isUpdating } = useUpdateAlert()

const isPending = ref(false)
watch([isCreating, isUpdating], ([c, u]) => { isPending.value = c || u })

// editAlert prop이 변경되면 수정 모드 전환
watch(
  () => props.editAlert,
  (alert) => {
    if (alert) {
      isEditMode.value = true
      editingId.value = alert.id
      form.value = {
        market: alert.market,
        indicator: alert.indicator,
        condition: alert.condition,
        threshold: alert.threshold,
        cooldown_minutes: alert.cooldown_minutes,
      }
    } else {
      resetForm()
    }
  },
)

// 지표 변경 시 조건 기본값 설정
watch(
  () => form.value.indicator,
  (ind) => {
    const conditions = INDICATOR_CONDITIONS[ind]
    if (conditions && conditions.length > 0) {
      form.value.condition = conditions[0]!.value
    }
  },
)

function handleSubmit() {
  if (isEditMode.value && editingId.value) {
    update(
      { id: editingId.value, data: form.value },
      { onSuccess: () => { resetForm(); emit('updated') } },
    )
  } else {
    create(form.value, {
      onSuccess: () => { resetForm(); emit('created') },
    })
  }
}

function resetForm() {
  isEditMode.value = false
  editingId.value = null
  form.value = { ...defaultForm }
}

function handleCancel() {
  resetForm()
  emit('cancel')
}

const indicators: IndicatorType[] = ['RSI', 'MACD', 'BB', 'PRICE', 'CHANGE_RATE']

const indicatorLabels: Record<string, string> = {
  RSI: 'RSI',
  MACD: 'MACD',
  BB: 'Bollinger Bands',
  PRICE: '가격 (Price)',
  CHANGE_RATE: '변동률 (Change Rate)',
}

const thresholdHints: Record<string, string> = {
  RSI: '0~100 (과매도: 30, 과매수: 70)',
  MACD: 'threshold 미사용 (크로스 감지)',
  BB: 'Bandwidth %',
  PRICE: 'KRW 가격',
  CHANGE_RATE: '변동률 % (예: 3 = 3%)',
}
</script>

<template>
  <form
    class="rounded-lg p-4 space-y-4"
    style="background-color: var(--color-bg-secondary)"
    @submit.prevent="handleSubmit"
  >
    <div class="flex items-center justify-between">
      <h3 class="text-sm font-medium">
        {{ isEditMode ? '알림 수정' : '새 알림 생성' }}
      </h3>
      <button
        v-if="isEditMode"
        type="button"
        class="text-xs px-2 py-1 rounded hover:bg-gray-600/30 transition-colors"
        style="color: var(--color-text-secondary)"
        @click="handleCancel"
      >
        취소
      </button>
    </div>

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
          <option v-for="ind in indicators" :key="ind" :value="ind">{{ indicatorLabels[ind] }}</option>
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
        <p class="text-[10px] mt-0.5" style="color: var(--color-text-secondary)">
          {{ thresholdHints[form.indicator] }}
        </p>
      </div>

      <!-- Cooldown -->
      <div class="col-span-2">
        <label class="text-xs" style="color: var(--color-text-secondary)">쿨다운 (분)</label>
        <input
          v-model.number="form.cooldown_minutes"
          type="number"
          min="0"
          step="5"
          class="mt-1 w-full rounded px-2 py-1.5 text-sm"
          style="background-color: var(--color-bg-tertiary); border: 1px solid var(--color-border); color: var(--color-text-primary)"
        />
        <p class="text-[10px] mt-0.5" style="color: var(--color-text-secondary)">
          같은 알림의 반복 발동 방지 (0 = 쿨다운 없음)
        </p>
      </div>
    </div>

    <button
      type="submit"
      :disabled="isPending"
      class="w-full py-2 rounded-lg text-sm font-medium text-white transition-colors disabled:opacity-50"
      :class="isEditMode ? 'bg-amber-500 hover:bg-amber-600' : 'bg-indigo-500 hover:bg-indigo-600'"
    >
      {{ isPending ? '처리 중...' : isEditMode ? '알림 수정' : '알림 생성' }}
    </button>
  </form>
</template>
