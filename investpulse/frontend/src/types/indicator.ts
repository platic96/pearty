export interface RSIData {
  values: number[]
  current: number | null
  signal: string
  window: number
}

export interface MACDData {
  macd_line: number[]
  signal_line: number[]
  histogram: number[]
  signal: string
}

export interface BollingerBandsData {
  upper: number[]
  middle: number[]
  lower: number[]
  signal: string
  bandwidth: number
}

export interface IndicatorData {
  rsi: RSIData
  macd: MACDData
  bollinger_bands: BollingerBandsData
  timestamps: string[]
}
