import apiClient from './client'
import type { KISStatus, StockCandle, StockPrice, StockSearchResult } from '@/types/stock'
import type { IndicatorData } from '@/types/indicator'

export const fetchKISStatus = () => apiClient.get<KISStatus>('/stocks/status')

export const searchStocks = (q: string) =>
  apiClient.get<StockSearchResult[]>('/stocks/search', { params: { q } })

export const fetchStockPrice = (stockCode: string) =>
  apiClient.get<StockPrice>(`/stocks/price/${stockCode}`)

export const fetchStockCandles = (stockCode: string, period = 'D', count = 100) =>
  apiClient.get<StockCandle[]>(`/stocks/candles/${stockCode}`, {
    params: { period, count },
  })

export const fetchStockIndicators = (stockCode: string, period = 'D', count = 200) =>
  apiClient.get<IndicatorData>(`/stocks/indicators/${stockCode}`, {
    params: { period, count },
  })
