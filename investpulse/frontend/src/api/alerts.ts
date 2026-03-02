import apiClient from './client'
import type { Alert, AlertCreate, AlertUpdate, BulkAlertAction } from '@/types/alert'
import type { AlertHistoryItem, AlertHistoryPage } from '@/types/alertHistory'

export const fetchAlerts = (params?: { market?: string; indicator?: string; is_active?: boolean }) =>
  apiClient.get<Alert[]>('/alerts', { params })

export const createAlert = (data: AlertCreate) => apiClient.post<Alert>('/alerts', data)

export const updateAlert = (id: number, data: AlertUpdate) =>
  apiClient.put<Alert>(`/alerts/${id}`, data)

export const deleteAlert = (id: number) => apiClient.delete(`/alerts/${id}`)

export const duplicateAlert = (id: number) => apiClient.post<Alert>(`/alerts/${id}/duplicate`)

export const bulkAlertAction = (data: BulkAlertAction) =>
  apiClient.post<{ affected: number; action: string }>('/alerts/bulk', data)

export const fetchAlertHistory = (params?: { page?: number; size?: number; market?: string; indicator?: string }) =>
  apiClient.get<AlertHistoryPage>('/alerts/history', { params })

export const fetchAlertItemHistory = (alertId: number, limit?: number) =>
  apiClient.get<AlertHistoryItem[]>(`/alerts/${alertId}/history`, { params: { limit } })
