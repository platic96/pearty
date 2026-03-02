export interface AlertHistoryItem {
  id: number
  alert_id: number
  triggered_at: string
  indicator_value: number | null
  threshold: number
  status: 'triggered' | 'sent' | 'failed'
  message: string | null
  market: string | null
  indicator: string | null
  condition: string | null
}

export interface AlertHistoryPage {
  items: AlertHistoryItem[]
  total: number
  page: number
  size: number
  pages: number
}
