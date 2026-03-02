export interface StockPrice {
  stock_code: string
  name: string
  price: number
  change: number
  change_pct: number
  volume: number
  market_cap: number
  high: number
  low: number
  open: number
  prev_close: number
}

export interface StockSearchResult {
  stock_code: string
  name: string
}

export interface StockCandle {
  timestamp: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}

export interface KISStatus {
  configured: boolean
  message: string
}
