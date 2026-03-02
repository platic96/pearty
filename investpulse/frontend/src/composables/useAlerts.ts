import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'
import {
  fetchAlerts,
  createAlert,
  deleteAlert,
  updateAlert,
  duplicateAlert,
  bulkAlertAction,
} from '@/api/alerts'
import type { AlertCreate, AlertUpdate, BulkAlertAction } from '@/types/alert'
import type { Ref } from 'vue'

export function useAlerts(params?: Ref<{ market?: string; indicator?: string; is_active?: boolean }>) {
  return useQuery({
    queryKey: ['alerts', params],
    queryFn: async () => {
      const { data } = await fetchAlerts(params?.value)
      return data
    },
  })
}

export function useCreateAlert() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: AlertCreate) => createAlert(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['alerts'] }),
  })
}

export function useUpdateAlert() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: AlertUpdate }) => updateAlert(id, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['alerts'] }),
  })
}

export function useDeleteAlert() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => deleteAlert(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['alerts'] }),
  })
}

export function useDuplicateAlert() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => duplicateAlert(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['alerts'] }),
  })
}

export function useBulkAlertAction() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: BulkAlertAction) => bulkAlertAction(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['alerts'] }),
  })
}
