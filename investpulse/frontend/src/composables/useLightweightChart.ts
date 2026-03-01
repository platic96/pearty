import { onMounted, onUnmounted, watch, type Ref } from 'vue'
import {
  createChart,
  CandlestickSeries,
  type IChartApi,
  type ISeriesApi,
  type CandlestickData,
  type Time,
  ColorType,
} from 'lightweight-charts'

export function useLightweightChart(
  containerRef: Ref<HTMLElement | null>,
  data: Ref<CandlestickData<Time>[]>,
) {
  // 차트 인스턴스를 ref()로 감싸지 않음 — Vue reactivity proxy가 차트를 깨뜨림
  let chart: IChartApi | null = null
  let series: ISeriesApi<'Candlestick'> | null = null

  onMounted(() => {
    if (!containerRef.value) return

    chart = createChart(containerRef.value, {
      layout: {
        background: { type: ColorType.Solid, color: '#1a1a2e' },
        textColor: '#d1d4dc',
      },
      grid: {
        vertLines: { color: '#2a2a4a' },
        horzLines: { color: '#2a2a4a' },
      },
      width: containerRef.value.clientWidth,
      height: 400,
      crosshair: {
        mode: 0,
      },
      timeScale: {
        borderColor: '#2a2a4a',
        timeVisible: true,
      },
      rightPriceScale: {
        borderColor: '#2a2a4a',
      },
    })

    series = chart.addSeries(CandlestickSeries, {
      upColor: '#26a69a',
      downColor: '#ef5350',
      borderVisible: false,
      wickUpColor: '#26a69a',
      wickDownColor: '#ef5350',
    })

    if (data.value.length > 0) {
      series.setData(data.value)
      chart.timeScale().fitContent()
    }

    // Resize observer
    const resizeObserver = new ResizeObserver((entries) => {
      for (const entry of entries) {
        chart?.applyOptions({ width: entry.contentRect.width })
      }
    })
    resizeObserver.observe(containerRef.value)

    // Store observer for cleanup
    ;(containerRef.value as any).__resizeObserver = resizeObserver
  })

  watch(data, (newData) => {
    if (series && newData.length > 0) {
      series.setData(newData)
      chart?.timeScale().fitContent()
    }
  })

  onUnmounted(() => {
    if (containerRef.value) {
      const obs = (containerRef.value as any).__resizeObserver
      obs?.disconnect()
    }
    chart?.remove()
    chart = null
    series = null
  })

  return {
    getChart: () => chart,
    getSeries: () => series,
  }
}
