<script setup lang="ts">
import { ref, computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { useUiStore } from '@/stores/ui'
import { storeToRefs } from 'pinia'
import { fetchCandles } from '@/api/market'
import { useLightweightChart } from '@/composables/useLightweightChart'
import type { CandlestickData, Time } from 'lightweight-charts'

const uiStore = useUiStore()
const { selectedMarket, selectedTimeframe } = storeToRefs(uiStore)

const chartContainer = ref<HTMLElement | null>(null)

const { data: rawCandles } = useQuery({
  queryKey: ['candles', selectedMarket, selectedTimeframe],
  queryFn: async () => {
    const { data } = await fetchCandles(selectedMarket.value, selectedTimeframe.value)
    return data
  },
  refetchInterval: 60000,
})

const chartData = computed<CandlestickData<Time>[]>(() => {
  if (!rawCandles.value) return []
  return rawCandles.value.map((c) => ({
    time: (new Date(c.timestamp + 'Z').getTime() / 1000) as Time,
    open: c.open,
    high: c.high,
    low: c.low,
    close: c.close,
  }))
})

useLightweightChart(chartContainer, chartData)
</script>

<template>
  <div
    ref="chartContainer"
    class="w-full rounded-lg"
    style="min-height: 400px; background-color: var(--color-bg-secondary)"
  />
</template>
