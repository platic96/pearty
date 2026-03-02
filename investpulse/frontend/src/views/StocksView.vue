<script setup lang="ts">
import { ref, computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { useLightweightChart } from '@/composables/useLightweightChart'
import { useKISStatus, useStockPrice, useStockSearch } from '@/composables/useStocks'
import { fetchStockCandles, fetchStockIndicators } from '@/api/stocks'
import { formatKRW } from '@/utils/formatters'
import { CHART_COLORS } from '@/utils/constants'
import type { CandlestickData, Time } from 'lightweight-charts'
import EmptyState from '@/components/common/EmptyState.vue'

const POPULAR_STOCKS = [
  { code: '005930', name: '삼성전자' },
  { code: '000660', name: 'SK하이닉스' },
  { code: '005380', name: '현대자동차' },
  { code: '035420', name: 'NAVER' },
  { code: '035720', name: '카카오' },
  { code: '068270', name: '셀트리온' },
  { code: '373220', name: 'LG에너지솔루션' },
  { code: '051910', name: 'LG화학' },
]

const selectedStockCode = ref('005930')
const selectedPeriod = ref('D')
const periods = [
  { value: 'D', label: '일봉' },
  { value: 'W', label: '주봉' },
  { value: 'M', label: '월봉' },
]

// KIS API 연결 상태
const { data: kisStatus } = useKISStatus()

// 종목 검색
const { keyword: searchKeyword, data: searchResults } = useStockSearch()
const showSearch = ref(false)

function selectStock(code: string) {
  selectedStockCode.value = code
  showSearch.value = false
  searchKeyword.value = ''
}

// 현재가
const { data: stockPrice } = useStockPrice(selectedStockCode)

// 캔들 차트
const chartContainer = ref<HTMLElement | null>(null)

const { data: rawCandles } = useQuery({
  queryKey: ['stock-candles', selectedStockCode, selectedPeriod],
  queryFn: async () => {
    const { data } = await fetchStockCandles(selectedStockCode.value, selectedPeriod.value)
    return data
  },
  enabled: () => !!kisStatus.value?.configured,
})

const chartData = computed<CandlestickData<Time>[]>(() => {
  if (!rawCandles.value) return []
  return rawCandles.value.map((c) => ({
    time: c.timestamp as unknown as Time,
    open: c.open,
    high: c.high,
    low: c.low,
    close: c.close,
  }))
})

useLightweightChart(chartContainer, chartData)

// 기술지표
const { data: indicators } = useQuery({
  queryKey: ['stock-indicators', selectedStockCode, selectedPeriod],
  queryFn: async () => {
    const { data } = await fetchStockIndicators(selectedStockCode.value, selectedPeriod.value)
    return data
  },
  enabled: () => !!kisStatus.value?.configured,
})

const activeIndicatorTab = ref<'RSI' | 'MACD'>('RSI')

const rsiSignalClass = computed(() => {
  const signal = indicators.value?.rsi.signal
  if (signal === 'overbought') return 'text-red-400'
  if (signal === 'oversold') return 'text-green-400'
  return 'text-gray-400'
})

const rsiSignalLabel: Record<string, string> = {
  overbought: '과매수 (Overbought)',
  oversold: '과매도 (Oversold)',
  neutral: '중립 (Neutral)',
}

const macdSignalClass = computed(() => {
  const signal = indicators.value?.macd.signal
  if (signal === 'bullish_cross') return 'text-green-400'
  if (signal === 'bearish_cross') return 'text-red-400'
  return 'text-gray-400'
})

const macdSignalLabel: Record<string, string> = {
  bullish_cross: '골든크로스 (Bullish)',
  bearish_cross: '데드크로스 (Bearish)',
  neutral: '중립 (Neutral)',
}

const stockDisplayName = computed(() => {
  if (stockPrice.value) return `${stockPrice.value.name} (${stockPrice.value.stock_code})`
  const found = POPULAR_STOCKS.find((s) => s.code === selectedStockCode.value)
  return found ? `${found.name} (${found.code})` : selectedStockCode.value
})
</script>

<template>
  <div class="space-y-4">
    <!-- API 미설정 안내 -->
    <div
      v-if="kisStatus && !kisStatus.configured"
      class="rounded-lg p-4 border border-amber-500/30"
      style="background-color: rgba(245, 158, 11, 0.1)"
    >
      <h3 class="font-semibold text-amber-400 mb-1">한국투자증권 API 미설정</h3>
      <p class="text-sm" style="color: var(--color-text-secondary)">
        주식 시세를 조회하려면 <code class="px-1 py-0.5 rounded text-xs" style="background-color: var(--color-bg-tertiary)">.env</code> 파일에
        <code class="px-1 py-0.5 rounded text-xs" style="background-color: var(--color-bg-tertiary)">KIS_APP_KEY</code>와
        <code class="px-1 py-0.5 rounded text-xs" style="background-color: var(--color-bg-tertiary)">KIS_APP_SECRET</code>을 설정해주세요.
      </p>
    </div>

    <!-- Stock Header -->
    <div class="flex items-center justify-between">
      <div>
        <div class="flex items-center gap-3">
          <h2 class="text-2xl font-bold">{{ stockDisplayName }}</h2>
          <button
            class="text-xs px-2 py-1 rounded border hover:bg-white/10"
            style="border-color: var(--color-border)"
            @click="showSearch = !showSearch"
          >
            종목 변경
          </button>
        </div>
        <div v-if="stockPrice" class="flex items-baseline gap-3 mt-1">
          <span class="text-3xl font-bold">
            {{ formatKRW(stockPrice.price) }}
          </span>
          <span
            class="text-lg font-medium"
            :class="stockPrice.change >= 0 ? 'text-green-400' : 'text-red-400'"
          >
            {{ stockPrice.change >= 0 ? '+' : '' }}{{ stockPrice.change_pct.toFixed(2) }}%
          </span>
          <span class="text-sm" style="color: var(--color-text-secondary)">
            거래량 {{ new Intl.NumberFormat('ko-KR').format(stockPrice.volume) }}
          </span>
        </div>
      </div>

      <!-- Period selector -->
      <div class="flex gap-1">
        <button
          v-for="p in periods"
          :key="p.value"
          class="px-3 py-1.5 text-sm rounded-lg transition-colors"
          :class="selectedPeriod === p.value ? 'bg-indigo-500 text-white' : 'hover:bg-white/10'"
          @click="selectedPeriod = p.value"
        >
          {{ p.label }}
        </button>
      </div>
    </div>

    <!-- Search Panel -->
    <div
      v-if="showSearch"
      class="rounded-lg p-4"
      style="background-color: var(--color-bg-secondary)"
    >
      <input
        v-model="searchKeyword"
        type="text"
        placeholder="종목명 또는 코드 검색..."
        class="w-full px-3 py-2 rounded-lg text-sm outline-none"
        style="background-color: var(--color-bg-tertiary); color: var(--color-text-primary)"
      />
      <!-- 검색 결과 -->
      <div v-if="searchResults && searchResults.length > 0" class="mt-2 space-y-1">
        <button
          v-for="result in searchResults"
          :key="result.stock_code"
          class="w-full text-left px-3 py-2 rounded hover:bg-white/10 text-sm flex justify-between"
          @click="selectStock(result.stock_code)"
        >
          <span>{{ result.name }}</span>
          <span style="color: var(--color-text-secondary)">{{ result.stock_code }}</span>
        </button>
      </div>
      <!-- 인기 종목 -->
      <div v-else class="mt-3">
        <p class="text-xs mb-2" style="color: var(--color-text-secondary)">주요 종목</p>
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-2">
          <button
            v-for="stock in POPULAR_STOCKS"
            :key="stock.code"
            class="px-3 py-2 rounded text-sm text-left hover:bg-white/10 transition-colors"
            :class="selectedStockCode === stock.code ? 'bg-indigo-500/20 border border-indigo-500/50' : ''"
            style="background-color: var(--color-bg-tertiary)"
            @click="selectStock(stock.code)"
          >
            <div class="font-medium">{{ stock.name }}</div>
            <div class="text-xs" style="color: var(--color-text-secondary)">{{ stock.code }}</div>
          </button>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="grid grid-cols-1 lg:grid-cols-4 gap-4">
      <!-- Chart + Indicators -->
      <div class="lg:col-span-3 space-y-4">
        <!-- Candle Chart -->
        <div
          v-if="kisStatus?.configured"
          ref="chartContainer"
          class="w-full rounded-lg"
          style="min-height: 400px; background-color: var(--color-bg-secondary)"
        />
        <EmptyState
          v-else
          title="차트를 표시할 수 없습니다"
          description="한국투자증권 API 키를 설정하면 실시간 차트를 볼 수 있습니다."
        />

        <!-- Indicator Panel -->
        <div
          v-if="indicators"
          class="rounded-lg p-4"
          style="background-color: var(--color-bg-secondary)"
        >
          <div class="flex gap-2 mb-4">
            <button
              class="px-3 py-1.5 text-sm rounded-lg transition-colors"
              :class="activeIndicatorTab === 'RSI' ? 'bg-indigo-500 text-white' : 'hover:bg-white/10'"
              @click="activeIndicatorTab = 'RSI'"
            >
              RSI
            </button>
            <button
              class="px-3 py-1.5 text-sm rounded-lg transition-colors"
              :class="activeIndicatorTab === 'MACD' ? 'bg-indigo-500 text-white' : 'hover:bg-white/10'"
              @click="activeIndicatorTab = 'MACD'"
            >
              MACD
            </button>
          </div>

          <!-- RSI -->
          <div v-if="activeIndicatorTab === 'RSI'">
            <div class="flex items-center justify-between mb-3">
              <div>
                <span class="text-2xl font-bold">{{ indicators.rsi.current?.toFixed(2) ?? '—' }}</span>
                <span class="text-sm ml-2" :class="rsiSignalClass">
                  {{ rsiSignalLabel[indicators.rsi.signal] || indicators.rsi.signal }}
                </span>
              </div>
            </div>
            <div class="relative h-4 rounded-full overflow-hidden" style="background-color: var(--color-bg-tertiary)">
              <div class="absolute top-0 left-[30%] w-px h-full bg-green-500/40" />
              <div class="absolute top-0 left-[70%] w-px h-full bg-red-500/40" />
              <div
                v-if="indicators.rsi.current != null"
                class="absolute top-0 h-full w-1 rounded-full"
                :style="{
                  left: `${indicators.rsi.current}%`,
                  backgroundColor: indicators.rsi.current > 70 ? CHART_COLORS.down : indicators.rsi.current < 30 ? CHART_COLORS.up : CHART_COLORS.accent,
                }"
              />
            </div>
            <div class="flex justify-between text-xs mt-1" style="color: var(--color-text-secondary)">
              <span>0 (과매도)</span>
              <span>50</span>
              <span>100 (과매수)</span>
            </div>
          </div>

          <!-- MACD -->
          <div v-if="activeIndicatorTab === 'MACD'">
            <div class="mb-3">
              <span class="text-sm" :class="macdSignalClass">
                {{ macdSignalLabel[indicators.macd.signal] || indicators.macd.signal }}
              </span>
            </div>
            <div class="flex items-end gap-px h-24">
              <div
                v-for="(val, idx) in indicators.macd.histogram.slice(-30)"
                :key="idx"
                class="flex-1 rounded-t-sm"
                :style="{
                  height: `${Math.min(Math.abs(val) / (Math.max(...indicators.macd.histogram.slice(-30).map(Math.abs)) || 1) * 100, 100)}%`,
                  backgroundColor: val >= 0 ? CHART_COLORS.macdHistUp : CHART_COLORS.macdHistDown,
                  alignSelf: val >= 0 ? 'flex-end' : 'flex-start',
                }"
              />
            </div>
          </div>

          <!-- Bollinger Bands -->
          <div class="mt-4 pt-4 border-t" style="border-color: var(--color-border)">
            <div class="flex items-center justify-between">
              <span class="text-sm font-medium">Bollinger Bands</span>
              <span
                class="text-xs px-2 py-0.5 rounded"
                :class="{
                  'bg-red-500/20 text-red-400': indicators.bollinger_bands.signal === 'above_upper',
                  'bg-green-500/20 text-green-400': indicators.bollinger_bands.signal === 'below_lower',
                  'bg-gray-500/20 text-gray-400': indicators.bollinger_bands.signal === 'neutral',
                }"
              >
                {{ indicators.bollinger_bands.signal === 'above_upper' ? '상단 이탈' : indicators.bollinger_bands.signal === 'below_lower' ? '하단 이탈' : '밴드 내' }}
              </span>
            </div>
            <div class="text-xs mt-1" style="color: var(--color-text-secondary)">
              Bandwidth: {{ indicators.bollinger_bands.bandwidth }}%
            </div>
          </div>
        </div>
      </div>

      <!-- Stock Info Sidebar -->
      <div class="lg:col-span-1 space-y-4">
        <!-- 종목 상세 -->
        <div v-if="stockPrice" class="rounded-lg p-4" style="background-color: var(--color-bg-secondary)">
          <h3 class="text-sm font-semibold mb-3">종목 정보</h3>
          <div class="space-y-2 text-sm">
            <div class="flex justify-between">
              <span style="color: var(--color-text-secondary)">시가</span>
              <span>{{ formatKRW(stockPrice.open) }}</span>
            </div>
            <div class="flex justify-between">
              <span style="color: var(--color-text-secondary)">고가</span>
              <span class="text-red-400">{{ formatKRW(stockPrice.high) }}</span>
            </div>
            <div class="flex justify-between">
              <span style="color: var(--color-text-secondary)">저가</span>
              <span class="text-green-400">{{ formatKRW(stockPrice.low) }}</span>
            </div>
            <div class="flex justify-between">
              <span style="color: var(--color-text-secondary)">전일종가</span>
              <span>{{ formatKRW(stockPrice.prev_close) }}</span>
            </div>
            <div class="flex justify-between">
              <span style="color: var(--color-text-secondary)">시가총액</span>
              <span>{{ formatKRW(stockPrice.market_cap * 100_000_000) }}</span>
            </div>
          </div>
        </div>

        <!-- 인기 종목 리스트 -->
        <div class="rounded-lg p-4" style="background-color: var(--color-bg-secondary)">
          <h3 class="text-sm font-semibold mb-3">주요 종목</h3>
          <div class="space-y-1">
            <button
              v-for="stock in POPULAR_STOCKS"
              :key="stock.code"
              class="w-full flex justify-between items-center px-2 py-1.5 rounded text-sm hover:bg-white/10 transition-colors"
              :class="selectedStockCode === stock.code ? 'bg-indigo-500/20' : ''"
              @click="selectStock(stock.code)"
            >
              <span>{{ stock.name }}</span>
              <span class="text-xs" style="color: var(--color-text-secondary)">{{ stock.code }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
