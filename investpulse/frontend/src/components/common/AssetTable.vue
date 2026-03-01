<script setup lang="ts">
import { useMarketStore } from '@/stores/market'
import { storeToRefs } from 'pinia'
import { useUiStore } from '@/stores/ui'
import { formatKRW, formatPercent } from '@/utils/formatters'
import { DEFAULT_MARKETS } from '@/utils/constants'

const marketStore = useMarketStore()
const uiStore = useUiStore()
const { prices } = storeToRefs(marketStore)
</script>

<template>
  <div class="rounded-lg p-4" style="background-color: var(--color-bg-secondary)">
    <h3 class="text-sm font-medium mb-3" style="color: var(--color-text-secondary)">Watchlist</h3>
    <div class="space-y-2">
      <button
        v-for="symbol in DEFAULT_MARKETS"
        :key="symbol"
        class="w-full flex items-center justify-between p-3 rounded-lg hover:bg-white/5 transition-colors"
        :class="{ 'bg-indigo-500/10 border border-indigo-500/30': uiStore.selectedMarket === symbol }"
        @click="uiStore.setMarket(symbol)"
      >
        <div class="flex items-center gap-3">
          <span class="font-medium text-sm">{{ symbol }}</span>
        </div>
        <div class="text-right">
          <div class="text-sm font-medium">
            {{ prices[symbol] ? formatKRW(prices[symbol].trade_price) : '—' }}
          </div>
          <div
            v-if="prices[symbol]"
            class="text-xs"
            :class="prices[symbol].signed_change_rate >= 0 ? 'text-green-400' : 'text-red-400'"
          >
            {{ formatPercent(prices[symbol].signed_change_rate) }}
          </div>
        </div>
      </button>
    </div>
  </div>
</template>
