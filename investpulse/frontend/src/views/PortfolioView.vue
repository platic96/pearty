<script setup lang="ts">
import { useQuery } from '@tanstack/vue-query'
import { fetchPortfolio } from '@/api/portfolio'
import { formatKRW, formatNumber } from '@/utils/formatters'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import '@/plugins/echarts'
import VChart from 'vue-echarts'
import { computed } from 'vue'

const { data: portfolio, isLoading } = useQuery({
  queryKey: ['portfolio'],
  queryFn: async () => {
    const { data } = await fetchPortfolio()
    return data
  },
  refetchInterval: 30000,
})

const pieOption = computed(() => {
  if (!portfolio.value?.assets.length) return null
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'item', formatter: '{b}: {d}%' },
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: true,
        itemStyle: { borderRadius: 6, borderColor: '#1a1a2e', borderWidth: 2 },
        label: { color: '#e0e0e0' },
        data: portfolio.value.assets.map((a) => ({
          name: a.symbol,
          value: a.current_price ? a.quantity * a.current_price : a.quantity * a.avg_buy_price,
        })),
      },
    ],
  }
})
</script>

<template>
  <div class="space-y-6">
    <h2 class="text-2xl font-bold">Portfolio</h2>

    <LoadingSpinner v-if="isLoading" />

    <template v-else-if="portfolio">
      <!-- Summary -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="rounded-lg p-4" style="background-color: var(--color-bg-secondary)">
          <p class="text-xs" style="color: var(--color-text-secondary)">총 투자금</p>
          <p class="text-xl font-bold mt-1">{{ formatKRW(portfolio.total_invested) }}</p>
        </div>
        <div class="rounded-lg p-4" style="background-color: var(--color-bg-secondary)">
          <p class="text-xs" style="color: var(--color-text-secondary)">현재 평가</p>
          <p class="text-xl font-bold mt-1">{{ formatKRW(portfolio.total_current_value) }}</p>
        </div>
        <div class="rounded-lg p-4" style="background-color: var(--color-bg-secondary)">
          <p class="text-xs" style="color: var(--color-text-secondary)">수익/손실</p>
          <p
            class="text-xl font-bold mt-1"
            :class="portfolio.total_profit_loss >= 0 ? 'text-green-400' : 'text-red-400'"
          >
            {{ portfolio.total_profit_loss >= 0 ? '+' : '' }}{{ formatKRW(portfolio.total_profit_loss) }}
          </p>
        </div>
        <div class="rounded-lg p-4" style="background-color: var(--color-bg-secondary)">
          <p class="text-xs" style="color: var(--color-text-secondary)">수익률</p>
          <p
            class="text-xl font-bold mt-1"
            :class="portfolio.total_profit_loss_pct >= 0 ? 'text-green-400' : 'text-red-400'"
          >
            {{ portfolio.total_profit_loss_pct >= 0 ? '+' : '' }}{{ portfolio.total_profit_loss_pct.toFixed(2) }}%
          </p>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Pie chart -->
        <div v-if="pieOption" class="rounded-lg p-4" style="background-color: var(--color-bg-secondary)">
          <h3 class="text-sm font-medium mb-2" style="color: var(--color-text-secondary)">자산 배분</h3>
          <VChart :option="pieOption" style="height: 250px" />
        </div>

        <!-- Asset table -->
        <div class="lg:col-span-2 rounded-lg p-4" style="background-color: var(--color-bg-secondary)">
          <h3 class="text-sm font-medium mb-3" style="color: var(--color-text-secondary)">보유 자산</h3>
          <EmptyState v-if="!portfolio.assets.length" message="등록된 자산이 없습니다." />
          <table v-else class="w-full text-sm">
            <thead>
              <tr style="color: var(--color-text-secondary)">
                <th class="text-left py-2">종목</th>
                <th class="text-right py-2">수량</th>
                <th class="text-right py-2">평균매수가</th>
                <th class="text-right py-2">현재가</th>
                <th class="text-right py-2">수익률</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="asset in portfolio.assets" :key="asset.id" class="border-t" style="border-color: var(--color-border)">
                <td class="py-3 font-medium">{{ asset.symbol }}</td>
                <td class="text-right py-3">{{ formatNumber(asset.quantity, 4) }}</td>
                <td class="text-right py-3">{{ formatKRW(asset.avg_buy_price) }}</td>
                <td class="text-right py-3">{{ asset.current_price ? formatKRW(asset.current_price) : '—' }}</td>
                <td
                  class="text-right py-3"
                  :class="(asset.profit_loss_pct ?? 0) >= 0 ? 'text-green-400' : 'text-red-400'"
                >
                  {{ asset.profit_loss_pct != null ? `${asset.profit_loss_pct >= 0 ? '+' : ''}${asset.profit_loss_pct.toFixed(2)}%` : '—' }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
  </div>
</template>
