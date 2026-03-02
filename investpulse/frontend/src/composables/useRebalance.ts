import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { ref, type Ref } from 'vue'
import {
  createTarget,
  deleteTarget,
  fetchRebalanceSuggestion,
  fetchTargets,
  initDefaultTargets,
  updateTarget,
} from '@/api/rebalance'
import type { TargetAllocationCreate, TargetAllocationUpdate } from '@/types/rebalance'

export function useTargetAllocations() {
  return useQuery({
    queryKey: ['target-allocations'],
    queryFn: () => fetchTargets().then((r) => r.data),
  })
}

export function useRebalanceSuggestion(threshold: Ref<number> = ref(5.0)) {
  return useQuery({
    queryKey: ['rebalance-suggestion', threshold],
    queryFn: () => fetchRebalanceSuggestion(threshold.value).then((r) => r.data),
  })
}

export function useInitDefaultTargets() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: () => initDefaultTargets().then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['target-allocations'] })
      queryClient.invalidateQueries({ queryKey: ['rebalance-suggestion'] })
    },
  })
}

export function useCreateTarget() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: TargetAllocationCreate) => createTarget(data).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['target-allocations'] })
      queryClient.invalidateQueries({ queryKey: ['rebalance-suggestion'] })
    },
  })
}

export function useUpdateTarget() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: TargetAllocationUpdate }) =>
      updateTarget(id, data).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['target-allocations'] })
      queryClient.invalidateQueries({ queryKey: ['rebalance-suggestion'] })
    },
  })
}

export function useDeleteTarget() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => deleteTarget(id).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['target-allocations'] })
      queryClient.invalidateQueries({ queryKey: ['rebalance-suggestion'] })
    },
  })
}
