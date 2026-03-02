import apiClient from './client'
import type {
  RebalanceSuggestion,
  TargetAllocation,
  TargetAllocationCreate,
  TargetAllocationUpdate,
} from '@/types/rebalance'

export const fetchTargets = () =>
  apiClient.get<TargetAllocation[]>('/rebalance/targets')

export const createTarget = (data: TargetAllocationCreate) =>
  apiClient.post<TargetAllocation>('/rebalance/targets', data)

export const updateTarget = (id: number, data: TargetAllocationUpdate) =>
  apiClient.put<TargetAllocation>(`/rebalance/targets/${id}`, data)

export const deleteTarget = (id: number) =>
  apiClient.delete(`/rebalance/targets/${id}`)

export const initDefaultTargets = () =>
  apiClient.post('/rebalance/targets/init-defaults')

export const fetchRebalanceSuggestion = (threshold = 5.0) =>
  apiClient.get<RebalanceSuggestion>('/rebalance/suggest', {
    params: { threshold },
  })
