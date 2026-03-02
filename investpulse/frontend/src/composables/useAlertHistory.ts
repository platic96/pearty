import { useQuery } from '@tanstack/vue-query'
import { fetchAlertHistory, fetchAlertItemHistory } from '@/api/alerts'
import type { Ref } from 'vue'

export function useAlertHistory(params: Ref<{ page: number; size: number; market?: string; indicator?: string }>) {
  return useQuery({
    queryKey: ['alertHistory', params],
    queryFn: async () => {
      const { data } = await fetchAlertHistory(params.value)
      return data
    },
  })
}

export function useAlertItemHistory(alertId: Ref<number | null>, limit = 20) {
  return useQuery({
    queryKey: ['alertItemHistory', alertId],
    queryFn: async () => {
      if (!alertId.value) return []
      const { data } = await fetchAlertItemHistory(alertId.value, limit)
      return data
    },
    enabled: () => alertId.value !== null,
  })
}
