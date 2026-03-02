import { useQuery } from '@tanstack/vue-query'
import { ref, type Ref } from 'vue'
import {
  fetchKISStatus,
  fetchStockCandles,
  fetchStockIndicators,
  fetchStockPrice,
  searchStocks,
} from '@/api/stocks'

export function useKISStatus() {
  return useQuery({
    queryKey: ['kis-status'],
    queryFn: () => fetchKISStatus().then((r) => r.data),
    staleTime: 60 * 1000,
  })
}

export function useStockPrice(stockCode: Ref<string>) {
  return useQuery({
    queryKey: ['stock-price', stockCode],
    queryFn: () => fetchStockPrice(stockCode.value).then((r) => r.data),
    enabled: () => !!stockCode.value,
    refetchInterval: 30_000,
  })
}

export function useStockCandles(stockCode: Ref<string>, period: Ref<string>) {
  return useQuery({
    queryKey: ['stock-candles', stockCode, period],
    queryFn: () => fetchStockCandles(stockCode.value, period.value).then((r) => r.data),
    enabled: () => !!stockCode.value,
  })
}

export function useStockIndicators(stockCode: Ref<string>, period: Ref<string>) {
  return useQuery({
    queryKey: ['stock-indicators', stockCode, period],
    queryFn: () => fetchStockIndicators(stockCode.value, period.value).then((r) => r.data),
    enabled: () => !!stockCode.value,
  })
}

export function useStockSearch() {
  const keyword = ref('')
  const query = useQuery({
    queryKey: ['stock-search', keyword],
    queryFn: () => searchStocks(keyword.value).then((r) => r.data),
    enabled: () => keyword.value.length >= 1,
  })

  return { keyword, ...query }
}
