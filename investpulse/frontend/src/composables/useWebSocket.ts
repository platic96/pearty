import { ref, onUnmounted } from 'vue'
import { useMarketStore } from '@/stores/market'
import { WS_MARKET_URL } from '@/api/client'

export function useWebSocket() {
  const isConnected = ref(false)
  const marketStore = useMarketStore()
  let ws: WebSocket | null = null
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null

  function connect() {
    ws = new WebSocket(WS_MARKET_URL)

    ws.onopen = () => {
      isConnected.value = true
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.market) {
          marketStore.updatePrice(data)
        }
      } catch {
        // ignore parse errors
      }
    }

    ws.onclose = () => {
      isConnected.value = false
      reconnectTimer = setTimeout(connect, 3000)
    }

    ws.onerror = () => {
      ws?.close()
    }
  }

  function disconnect() {
    if (reconnectTimer) clearTimeout(reconnectTimer)
    ws?.close()
  }

  connect()
  onUnmounted(disconnect)

  return { isConnected, disconnect }
}
