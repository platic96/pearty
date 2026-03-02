import apiClient from './client'
import type { PortfolioAsset, PortfolioAssetCreate, PortfolioSummary } from '@/types/portfolio'

export const fetchPortfolio = () => apiClient.get<PortfolioSummary>('/portfolio')

export const addPortfolioAsset = (data: PortfolioAssetCreate) =>
  apiClient.post<PortfolioAsset>('/portfolio/assets', data)

export const updatePortfolioAsset = (id: number, data: Partial<PortfolioAssetCreate>) =>
  apiClient.put<PortfolioAsset>(`/portfolio/assets/${id}`, data)

export const deletePortfolioAsset = (id: number) =>
  apiClient.delete(`/portfolio/assets/${id}`)
