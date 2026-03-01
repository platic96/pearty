export const CHART_COLORS = {
  up: '#26a69a',
  down: '#ef5350',
  bg: '#1a1a2e',
  grid: '#2a2a4a',
  text: '#d1d4dc',
  accent: '#6366f1',
  rsi: '#e1bee7',
  macdLine: '#42a5f5',
  macdSignal: '#ff7043',
  macdHistUp: '#26a69a',
  macdHistDown: '#ef5350',
  bbUpper: '#7986cb',
  bbMiddle: '#9e9e9e',
  bbLower: '#7986cb',
}

export const DEFAULT_MARKETS = ['BTC', 'ETH', 'XRP', 'SOL', 'DOGE']

export const INDICATOR_CONDITIONS = {
  RSI: [
    { value: 'above', label: '이상 (Above)' },
    { value: 'below', label: '이하 (Below)' },
  ],
  MACD: [
    { value: 'cross_up', label: '골든크로스 (Golden Cross)' },
    { value: 'cross_down', label: '데드크로스 (Dead Cross)' },
  ],
  BB: [
    { value: 'above', label: '상단 이탈 (Above Upper)' },
    { value: 'below', label: '하단 이탈 (Below Lower)' },
  ],
  PRICE: [
    { value: 'above', label: '이상 (Above)' },
    { value: 'below', label: '이하 (Below)' },
  ],
}
