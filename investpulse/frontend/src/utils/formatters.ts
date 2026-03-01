/**
 * 통화 포맷 (KRW)
 */
export function formatKRW(value: number): string {
  if (value >= 1_000_000_000) {
    return `${(value / 1_000_000_000).toFixed(2)}B`
  }
  if (value >= 1_000_000) {
    return `${(value / 1_000_000).toFixed(1)}M`
  }
  return new Intl.NumberFormat('ko-KR', {
    style: 'currency',
    currency: 'KRW',
    maximumFractionDigits: 0,
  }).format(value)
}

/**
 * 퍼센트 포맷
 */
export function formatPercent(value: number): string {
  const sign = value >= 0 ? '+' : ''
  return `${sign}${(value * 100).toFixed(2)}%`
}

/**
 * 숫자 포맷
 */
export function formatNumber(value: number, decimals = 2): string {
  return new Intl.NumberFormat('ko-KR', {
    maximumFractionDigits: decimals,
  }).format(value)
}
