import apiClient from './client'
import type { PortfolioAssetCreate, PortfolioSummary } from '@/types/portfolio'

export const fetchPortfolio = () => apiClient.get<PortfolioSummary>('/portfolio')

export const addPortfolioAsset = (data: PortfolioAssetCreate) =>
  apiClient.post('/portfolio/assets', data)

export const deletePortfolioAsset = (id: number) =>
  apiClient.delete(`/portfolio/assets/${id}`)
