import apiClient from './client'
import type { Alert, AlertCreate, AlertUpdate } from '@/types/alert'

export const fetchAlerts = () => apiClient.get<Alert[]>('/alerts')

export const createAlert = (data: AlertCreate) => apiClient.post<Alert>('/alerts', data)

export const updateAlert = (id: number, data: AlertUpdate) =>
  apiClient.put<Alert>(`/alerts/${id}`, data)

export const deleteAlert = (id: number) => apiClient.delete(`/alerts/${id}`)
