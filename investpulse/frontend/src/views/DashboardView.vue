<script setup lang="ts">
import { computed } from 'vue'
import { useUiStore } from '@/stores/ui'
import { useMarketStore } from '@/stores/market'
import { storeToRefs } from 'pinia'
import CandleChart from '@/components/charts/CandleChart.vue'
import IndicatorPanel from '@/components/charts/IndicatorPanel.vue'
import AssetTable from '@/components/common/AssetTable.vue'
import { formatKRW, formatPercent } from '@/utils/formatters'

const uiStore = useUiStore()
const marketStore = useMarketStore()
const { selectedMarket } = storeToRefs(uiStore)
const { prices } = storeToRefs(marketStore)

const currentPrice = computed(() => prices.value[selectedMarket.value])
</script>

<template>
  <div class="space-y-4">
    <!-- Price Header -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-2xl font-bold">{{ selectedMarket }}/KRW</h2>
        <div class="flex items-baseline gap-3 mt-1">
          <span class="text-3xl font-bold">
            {{ currentPrice ? formatKRW(currentPrice.trade_price) : '—' }}
          </span>
          <span
            v-if="currentPrice"
            class="text-lg font-medium"
            :class="currentPrice.signed_change_rate >= 0 ? 'text-green-400' : 'text-red-400'"
          >
            {{ formatPercent(currentPrice.signed_change_rate) }}
          </span>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="grid grid-cols-1 lg:grid-cols-4 gap-4">
      <!-- Chart + Indicators -->
      <div class="lg:col-span-3 space-y-4">
        <CandleChart />
        <IndicatorPanel />
      </div>

      <!-- Watchlist sidebar -->
      <div class="lg:col-span-1">
        <AssetTable />
      </div>
    </div>
  </div>
</template>
