import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { RealtimePrice } from '@/types/market'

export const useMarketStore = defineStore('market', () => {
  const prices = ref<Record<string, RealtimePrice>>({})
  const lastUpdated = ref<Date | null>(null)

  function updatePrice(data: RealtimePrice) {
    const symbol = data.market?.replace('KRW-', '')
    if (symbol) {
      prices.value[symbol] = data
      lastUpdated.value = new Date()
    }
  }

  function getPrice(symbol: string): RealtimePrice | undefined {
    return prices.value[symbol]
  }

  return { prices, lastUpdated, updatePrice, getPrice }
})
