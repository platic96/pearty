export type IndicatorType = 'RSI' | 'MACD' | 'BB' | 'PRICE' | 'CHANGE_RATE'

export interface Alert {
  id: number
  market: string
  indicator: IndicatorType
  condition: string
  threshold: number
  is_active: boolean
  cooldown_minutes: number
  last_triggered_at: string | null
  trigger_count: number
  created_at: string
  updated_at: string
}

export interface AlertCreate {
  market: string
  indicator: IndicatorType
  condition: string
  threshold: number
  cooldown_minutes?: number
}

export interface AlertUpdate {
  market?: string
  indicator?: IndicatorType
  condition?: string
  threshold?: number
  is_active?: boolean
  cooldown_minutes?: number
}

export interface BulkAlertAction {
  alert_ids: number[]
  action: 'activate' | 'deactivate' | 'delete'
}
