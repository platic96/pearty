import apiClient from './client'
import type { Candle, MarketInfo, Ticker } from '@/types/market'
import type { IndicatorData } from '@/types/indicator'

export const fetchMarkets = () => apiClient.get<MarketInfo[]>('/market/markets')

export const fetchCryptoPrice = (symbol: string) =>
  apiClient.get<Ticker>(`/market/crypto/${symbol}`)

export const fetchCandles = (symbol: string, timeframe = '1d', count = 200) =>
  apiClient.get<Candle[]>(`/market/candles/${symbol}`, {
    params: { timeframe, count },
  })

export const fetchIndicators = (symbol: string, timeframe = '1d') =>
  apiClient.get<IndicatorData>(`/indicators/${symbol}`, {
    params: { timeframe },
  })
