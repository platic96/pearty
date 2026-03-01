export interface Alert {
  id: number
  market: string
  indicator: 'RSI' | 'MACD' | 'BB' | 'PRICE'
  condition: string
  threshold: number
  is_active: boolean
  last_triggered_at: string | null
  created_at: string
  updated_at: string
}

export interface AlertCreate {
  market: string
  indicator: 'RSI' | 'MACD' | 'BB' | 'PRICE'
  condition: string
  threshold: number
}

export interface AlertUpdate {
  market?: string
  indicator?: 'RSI' | 'MACD' | 'BB' | 'PRICE'
  condition?: string
  threshold?: number
  is_active?: boolean
}
