import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUiStore = defineStore('ui', () => {
  const selectedMarket = ref('BTC')
  const selectedTimeframe = ref('1d')
  const sidebarOpen = ref(true)

  const timeframes = ['1m', '5m', '15m', '1h', '4h', '1d', '1w']

  function setMarket(market: string) {
    selectedMarket.value = market
  }

  function setTimeframe(tf: string) {
    selectedTimeframe.value = tf
  }

  function toggleSidebar() {
    sidebarOpen.value = !sidebarOpen.value
  }

  return { selectedMarket, selectedTimeframe, sidebarOpen, timeframes, setMarket, setTimeframe, toggleSidebar }
})
