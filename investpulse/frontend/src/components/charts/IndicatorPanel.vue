<script setup lang="ts">
import { ref, computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { useUiStore } from '@/stores/ui'
import { storeToRefs } from 'pinia'
import { fetchIndicators } from '@/api/market'
import { CHART_COLORS } from '@/utils/constants'

const uiStore = useUiStore()
const { selectedMarket, selectedTimeframe } = storeToRefs(uiStore)
const activeTab = ref<'RSI' | 'MACD'>('RSI')

const { data: indicators } = useQuery({
  queryKey: ['indicators', selectedMarket, selectedTimeframe],
  queryFn: async () => {
    const { data } = await fetchIndicators(selectedMarket.value, selectedTimeframe.value)
    return data
  },
  refetchInterval: 60000,
})

const rsiSignalClass = computed(() => {
  const signal = indicators.value?.rsi.signal
  if (signal === 'overbought') return 'text-red-400'
  if (signal === 'oversold') return 'text-green-400'
  return 'text-gray-400'
})

const macdSignalClass = computed(() => {
  const signal = indicators.value?.macd.signal
  if (signal === 'bullish_cross') return 'text-green-400'
  if (signal === 'bearish_cross') return 'text-red-400'
  return 'text-gray-400'
})

const rsiSignalLabel: Record<string, string> = {
  overbought: '과매수 (Overbought)',
  oversold: '과매도 (Oversold)',
  neutral: '중립 (Neutral)',
}

const macdSignalLabel: Record<string, string> = {
  bullish_cross: '골든크로스 (Bullish)',
  bearish_cross: '데드크로스 (Bearish)',
  neutral: '중립 (Neutral)',
}
</script>

<template>
  <div class="rounded-lg p-4" style="background-color: var(--color-bg-secondary)">
    <!-- Tab -->
    <div class="flex gap-2 mb-4">
      <button
        class="px-3 py-1.5 text-sm rounded-lg transition-colors"
        :class="activeTab === 'RSI' ? 'bg-indigo-500 text-white' : 'hover:bg-white/10'"
        @click="activeTab = 'RSI'"
      >
        RSI
      </button>
      <button
        class="px-3 py-1.5 text-sm rounded-lg transition-colors"
        :class="activeTab === 'MACD' ? 'bg-indigo-500 text-white' : 'hover:bg-white/10'"
        @click="activeTab = 'MACD'"
      >
        MACD
      </button>
    </div>

    <!-- RSI -->
    <div v-if="activeTab === 'RSI' && indicators">
      <div class="flex items-center justify-between mb-3">
        <div>
          <span class="text-2xl font-bold">{{ indicators.rsi.current?.toFixed(2) ?? '—' }}</span>
          <span class="text-sm ml-2" :class="rsiSignalClass">
            {{ rsiSignalLabel[indicators.rsi.signal] || indicators.rsi.signal }}
          </span>
        </div>
        <span class="text-xs" style="color: var(--color-text-secondary)">Window: {{ indicators.rsi.window }}</span>
      </div>
      <!-- RSI bar indicator -->
      <div class="relative h-4 rounded-full overflow-hidden" style="background-color: var(--color-bg-tertiary)">
        <div class="absolute top-0 left-[30%] w-px h-full bg-green-500/40" />
        <div class="absolute top-0 left-[70%] w-px h-full bg-red-500/40" />
        <div
          v-if="indicators.rsi.current != null"
          class="absolute top-0 h-full w-1 rounded-full"
          :style="{
            left: `${indicators.rsi.current}%`,
            backgroundColor: indicators.rsi.current > 70 ? CHART_COLORS.down : indicators.rsi.current < 30 ? CHART_COLORS.up : CHART_COLORS.accent,
          }"
        />
      </div>
      <div class="flex justify-between text-xs mt-1" style="color: var(--color-text-secondary)">
        <span>0 (과매도)</span>
        <span>50</span>
        <span>100 (과매수)</span>
      </div>
    </div>

    <!-- MACD -->
    <div v-if="activeTab === 'MACD' && indicators">
      <div class="flex items-center justify-between mb-3">
        <div>
          <span class="text-sm" :class="macdSignalClass">
            {{ macdSignalLabel[indicators.macd.signal] || indicators.macd.signal }}
          </span>
        </div>
      </div>
      <!-- MACD 히스토그램 (최근 30개) -->
      <div class="flex items-end gap-px h-24">
        <div
          v-for="(val, idx) in indicators.macd.histogram.slice(-30)"
          :key="idx"
          class="flex-1 rounded-t-sm"
          :style="{
            height: `${Math.min(Math.abs(val) / (Math.max(...indicators.macd.histogram.slice(-30).map(Math.abs)) || 1) * 100, 100)}%`,
            backgroundColor: val >= 0 ? CHART_COLORS.macdHistUp : CHART_COLORS.macdHistDown,
            alignSelf: val >= 0 ? 'flex-end' : 'flex-start',
          }"
        />
      </div>
    </div>

    <!-- Bollinger Bands -->
    <div v-if="indicators" class="mt-4 pt-4 border-t" style="border-color: var(--color-border)">
      <div class="flex items-center justify-between">
        <span class="text-sm font-medium">Bollinger Bands</span>
        <span
          class="text-xs px-2 py-0.5 rounded"
          :class="{
            'bg-red-500/20 text-red-400': indicators.bollinger_bands.signal === 'above_upper',
            'bg-green-500/20 text-green-400': indicators.bollinger_bands.signal === 'below_lower',
            'bg-gray-500/20 text-gray-400': indicators.bollinger_bands.signal === 'neutral',
          }"
        >
          {{ indicators.bollinger_bands.signal === 'above_upper' ? '상단 이탈' : indicators.bollinger_bands.signal === 'below_lower' ? '하단 이탈' : '밴드 내' }}
        </span>
      </div>
      <div class="text-xs mt-1" style="color: var(--color-text-secondary)">
        Bandwidth: {{ indicators.bollinger_bands.bandwidth }}%
      </div>
    </div>
  </div>
</template>
