export interface Candle {
  timestamp: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}

export interface Ticker {
  market: string
  trade_price: number
  signed_change_rate: number
  acc_trade_volume_24h: number
  high_price: number
  low_price: number
  timestamp: number
}

export interface MarketInfo {
  market: string
  korean_name: string
  english_name: string
}

export interface RealtimePrice {
  market: string
  trade_price: number
  signed_change_rate: number
  acc_trade_volume_24h: number
  trade_timestamp: number
}
