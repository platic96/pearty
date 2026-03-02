<script setup lang="ts">
import { ref, computed } from 'vue'
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'
import { fetchPortfolio, addPortfolioAsset, deletePortfolioAsset } from '@/api/portfolio'
import { formatKRW, formatNumber } from '@/utils/formatters'
import { useRebalanceSuggestion, useTargetAllocations, useInitDefaultTargets } from '@/composables/useRebalance'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import '@/plugins/echarts'
import VChart from 'vue-echarts'
import type { AssetType, PortfolioAssetCreate } from '@/types/portfolio'

const queryClient = useQueryClient()

// ── 포트폴리오 데이터 ──
const { data: portfolio, isLoading } = useQuery({
  queryKey: ['portfolio'],
  queryFn: async () => {
    const { data } = await fetchPortfolio()
    return data
  },
  refetchInterval: 30000,
})

// ── 탭 관리 ──
const activeTab = ref<'overview' | 'rebalance'>('overview')

// ── 자산 추가 폼 ──
const showAddForm = ref(false)
const assetForm = ref<PortfolioAssetCreate>({
  symbol: '',
  asset_type: 'crypto',
  name: '',
  quantity: 0,
  avg_buy_price: 0,
  asset_class: '',
})

const assetTypeOptions: { value: AssetType; label: string }[] = [
  { value: 'crypto', label: '암호화폐' },
  { value: 'stock', label: '주식' },
  { value: 'cash_bond', label: '현금/채권' },
]

const addMutation = useMutation({
  mutationFn: (data: PortfolioAssetCreate) => addPortfolioAsset(data),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['portfolio'] })
    queryClient.invalidateQueries({ queryKey: ['rebalance-suggestion'] })
    showAddForm.value = false
    assetForm.value = { symbol: '', asset_type: 'crypto', name: '', quantity: 0, avg_buy_price: 0, asset_class: '' }
  },
})

const deleteMutation = useMutation({
  mutationFn: (id: number) => deletePortfolioAsset(id),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['portfolio'] })
    queryClient.invalidateQueries({ queryKey: ['rebalance-suggestion'] })
  },
})

function handleAddAsset() {
  if (!assetForm.value.symbol || assetForm.value.quantity <= 0) return
  addMutation.mutate(assetForm.value)
}

// ── 차트 옵션 ──
// 자산군별 파이차트
const groupPieOption = computed(() => {
  if (!portfolio.value?.groups.length) return null
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'item', formatter: '{b}: {d}%' },
    legend: { bottom: 0, textStyle: { color: '#d1d4dc' } },
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: true,
        itemStyle: { borderRadius: 6, borderColor: '#1a1a2e', borderWidth: 2 },
        label: { show: false },
        data: portfolio.value.groups.map((g) => ({
          name: g.label,
          value: Math.round(g.total_current_value),
        })),
      },
    ],
  }
})

// 개별 자산 파이차트
const assetPieOption = computed(() => {
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
        label: { color: '#e0e0e0', fontSize: 11 },
        data: portfolio.value.assets.map((a) => ({
          name: a.name || a.symbol,
          value: a.current_price ? Math.round(a.quantity * a.current_price) : Math.round(a.quantity * a.avg_buy_price),
        })),
      },
    ],
  }
})

// ── 리밸런싱 ──
const rebalanceThreshold = ref(5.0)
const { data: targets } = useTargetAllocations()
const { data: rebalanceSuggestion, isLoading: rebalanceLoading } = useRebalanceSuggestion(rebalanceThreshold)
const initTargets = useInitDefaultTargets()

const ASSET_TYPE_LABEL: Record<string, string> = {
  crypto: '암호화폐',
  stock: '주식',
  cash_bond: '현금/채권',
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <h2 class="text-2xl font-bold">포트폴리오</h2>
      <div class="flex gap-2">
        <button
          class="px-3 py-1.5 text-sm rounded-lg transition-colors"
          :class="activeTab === 'overview' ? 'bg-indigo-500 text-white' : 'hover:bg-white/10'"
          @click="activeTab = 'overview'"
        >
          현황 보기
        </button>
        <button
          class="px-3 py-1.5 text-sm rounded-lg transition-colors"
          :class="activeTab === 'rebalance' ? 'bg-indigo-500 text-white' : 'hover:bg-white/10'"
          @click="activeTab = 'rebalance'"
        >
          리밸런싱
        </button>
      </div>
    </div>

    <LoadingSpinner v-if="isLoading" />

    <template v-else-if="portfolio">
      <!-- Summary Cards -->
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

      <!-- ═══ Overview Tab ═══ -->
      <template v-if="activeTab === 'overview'">
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <!-- Charts -->
          <div class="space-y-4">
            <!-- 자산군별 파이 -->
            <div v-if="groupPieOption" class="rounded-lg p-4" style="background-color: var(--color-bg-secondary)">
              <h3 class="text-sm font-medium mb-2" style="color: var(--color-text-secondary)">자산군별 배분</h3>
              <VChart :option="groupPieOption" style="height: 250px" />
            </div>
            <!-- 개별 자산 파이 -->
            <div v-if="assetPieOption" class="rounded-lg p-4" style="background-color: var(--color-bg-secondary)">
              <h3 class="text-sm font-medium mb-2" style="color: var(--color-text-secondary)">개별 자산 배분</h3>
              <VChart :option="assetPieOption" style="height: 250px" />
            </div>
          </div>

          <!-- Asset Table -->
          <div class="lg:col-span-2 space-y-4">
            <!-- 자산 추가 버튼 -->
            <div class="flex justify-end">
              <button
                class="px-3 py-1.5 text-sm rounded-lg bg-indigo-500 text-white hover:bg-indigo-600 transition-colors"
                @click="showAddForm = !showAddForm"
              >
                {{ showAddForm ? '취소' : '+ 자산 추가' }}
              </button>
            </div>

            <!-- 자산 추가 폼 -->
            <div v-if="showAddForm" class="rounded-lg p-4" style="background-color: var(--color-bg-secondary)">
              <h3 class="text-sm font-semibold mb-3">자산 추가</h3>
              <div class="grid grid-cols-2 gap-3">
                <div>
                  <label class="text-xs block mb-1" style="color: var(--color-text-secondary)">자산 유형</label>
                  <select
                    v-model="assetForm.asset_type"
                    class="w-full px-2 py-1.5 rounded text-sm"
                    style="background-color: var(--color-bg-tertiary); color: var(--color-text-primary)"
                  >
                    <option v-for="opt in assetTypeOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
                  </select>
                </div>
                <div>
                  <label class="text-xs block mb-1" style="color: var(--color-text-secondary)">
                    {{ assetForm.asset_type === 'stock' ? '종목코드' : '심볼' }}
                  </label>
                  <input
                    v-model="assetForm.symbol"
                    type="text"
                    :placeholder="assetForm.asset_type === 'stock' ? '005930' : 'BTC'"
                    class="w-full px-2 py-1.5 rounded text-sm"
                    style="background-color: var(--color-bg-tertiary); color: var(--color-text-primary)"
                  />
                </div>
                <div>
                  <label class="text-xs block mb-1" style="color: var(--color-text-secondary)">종목명</label>
                  <input
                    v-model="assetForm.name"
                    type="text"
                    placeholder="삼성전자"
                    class="w-full px-2 py-1.5 rounded text-sm"
                    style="background-color: var(--color-bg-tertiary); color: var(--color-text-primary)"
                  />
                </div>
                <div>
                  <label class="text-xs block mb-1" style="color: var(--color-text-secondary)">세부 분류</label>
                  <input
                    v-model="assetForm.asset_class"
                    type="text"
                    placeholder="domestic_growth"
                    class="w-full px-2 py-1.5 rounded text-sm"
                    style="background-color: var(--color-bg-tertiary); color: var(--color-text-primary)"
                  />
                </div>
                <div>
                  <label class="text-xs block mb-1" style="color: var(--color-text-secondary)">수량</label>
                  <input
                    v-model.number="assetForm.quantity"
                    type="number"
                    step="any"
                    class="w-full px-2 py-1.5 rounded text-sm"
                    style="background-color: var(--color-bg-tertiary); color: var(--color-text-primary)"
                  />
                </div>
                <div>
                  <label class="text-xs block mb-1" style="color: var(--color-text-secondary)">평균 매수가 (원)</label>
                  <input
                    v-model.number="assetForm.avg_buy_price"
                    type="number"
                    step="any"
                    class="w-full px-2 py-1.5 rounded text-sm"
                    style="background-color: var(--color-bg-tertiary); color: var(--color-text-primary)"
                  />
                </div>
              </div>
              <div class="mt-3 flex justify-end">
                <button
                  class="px-4 py-1.5 text-sm rounded-lg bg-indigo-500 text-white hover:bg-indigo-600 disabled:opacity-50"
                  :disabled="!assetForm.symbol || assetForm.quantity <= 0 || addMutation.isPending.value"
                  @click="handleAddAsset"
                >
                  추가
                </button>
              </div>
            </div>

            <!-- 자산군별 그룹 테이블 -->
            <div
              v-for="group in portfolio.groups"
              :key="group.asset_type"
              class="rounded-lg p-4"
              style="background-color: var(--color-bg-secondary)"
            >
              <div class="flex items-center justify-between mb-3">
                <h3 class="text-sm font-semibold">
                  {{ group.label }}
                  <span class="text-xs font-normal ml-2" style="color: var(--color-text-secondary)">
                    (비중 {{ group.weight_pct.toFixed(1) }}%)
                  </span>
                </h3>
                <span
                  class="text-sm font-medium"
                  :class="group.profit_loss >= 0 ? 'text-green-400' : 'text-red-400'"
                >
                  {{ group.profit_loss >= 0 ? '+' : '' }}{{ group.profit_loss_pct.toFixed(2) }}%
                </span>
              </div>
              <table class="w-full text-sm">
                <thead>
                  <tr style="color: var(--color-text-secondary)">
                    <th class="text-left py-2">종목</th>
                    <th class="text-right py-2">수량</th>
                    <th class="text-right py-2">평균매수가</th>
                    <th class="text-right py-2">현재가</th>
                    <th class="text-right py-2">수익률</th>
                    <th class="text-right py-2 w-10"></th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="asset in group.assets"
                    :key="asset.id"
                    class="border-t"
                    style="border-color: var(--color-border)"
                  >
                    <td class="py-3">
                      <div class="font-medium">{{ asset.name || asset.symbol }}</div>
                      <div class="text-xs" style="color: var(--color-text-secondary)">{{ asset.symbol }}</div>
                    </td>
                    <td class="text-right py-3">{{ formatNumber(asset.quantity, 4) }}</td>
                    <td class="text-right py-3">{{ formatKRW(asset.avg_buy_price) }}</td>
                    <td class="text-right py-3">{{ asset.current_price ? formatKRW(asset.current_price) : '—' }}</td>
                    <td
                      class="text-right py-3"
                      :class="(asset.profit_loss_pct ?? 0) >= 0 ? 'text-green-400' : 'text-red-400'"
                    >
                      {{ asset.profit_loss_pct != null ? `${asset.profit_loss_pct >= 0 ? '+' : ''}${asset.profit_loss_pct.toFixed(2)}%` : '—' }}
                    </td>
                    <td class="text-right py-3">
                      <button
                        class="text-red-400 hover:text-red-300 text-xs"
                        @click="deleteMutation.mutate(asset.id)"
                      >
                        삭제
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- 자산이 없을 때 -->
            <EmptyState
              v-if="!portfolio.assets.length"
              title="등록된 자산이 없습니다"
              description="위의 '자산 추가' 버튼을 눌러 보유 자산을 등록하세요."
            />
          </div>
        </div>
      </template>

      <!-- ═══ Rebalance Tab ═══ -->
      <template v-if="activeTab === 'rebalance'">
        <!-- 목표 배분 미설정 안내 -->
        <div v-if="targets && targets.length === 0" class="rounded-lg p-6 text-center" style="background-color: var(--color-bg-secondary)">
          <p class="mb-3">목표 자산배분이 설정되지 않았습니다.</p>
          <p class="text-sm mb-4" style="color: var(--color-text-secondary)">
            개인 전략 템플릿을 기반으로 기본 목표 배분을 초기화하시겠습니까?
          </p>
          <button
            class="px-4 py-2 rounded-lg bg-indigo-500 text-white text-sm hover:bg-indigo-600 disabled:opacity-50"
            :disabled="initTargets.isPending.value"
            @click="initTargets.mutate()"
          >
            기본 목표 배분 초기화
          </button>
        </div>

        <template v-else>
          <!-- 리밸런싱 임계값 설정 -->
          <div class="flex items-center gap-4">
            <label class="text-sm" style="color: var(--color-text-secondary)">리밸런싱 기준:</label>
            <div class="flex items-center gap-2">
              <input
                v-model.number="rebalanceThreshold"
                type="range"
                min="1"
                max="20"
                step="1"
                class="w-32"
              />
              <span class="text-sm font-medium">±{{ rebalanceThreshold }}%</span>
            </div>
          </div>

          <LoadingSpinner v-if="rebalanceLoading" />

          <template v-else-if="rebalanceSuggestion">
            <!-- 요약 배너 -->
            <div
              class="rounded-lg p-4 border"
              :class="rebalanceSuggestion.needs_rebalance ? 'border-amber-500/30' : 'border-green-500/30'"
              :style="rebalanceSuggestion.needs_rebalance ? 'background-color: rgba(245,158,11,0.1)' : 'background-color: rgba(34,197,94,0.1)'"
            >
              <div class="flex items-center gap-2 mb-1">
                <span
                  class="text-lg"
                  :class="rebalanceSuggestion.needs_rebalance ? 'text-amber-400' : 'text-green-400'"
                >
                  {{ rebalanceSuggestion.needs_rebalance ? '리밸런싱 필요' : '배분 양호' }}
                </span>
              </div>
              <p class="text-sm" style="color: var(--color-text-secondary)">{{ rebalanceSuggestion.summary }}</p>
              <p class="text-xs mt-1" style="color: var(--color-text-secondary)">
                전체 포트폴리오 가치: {{ formatKRW(rebalanceSuggestion.total_portfolio_value) }}
              </p>
            </div>

            <!-- 리밸런싱 테이블 -->
            <div class="rounded-lg p-4" style="background-color: var(--color-bg-secondary)">
              <h3 class="text-sm font-semibold mb-3">자산배분 상세</h3>
              <table class="w-full text-sm">
                <thead>
                  <tr style="color: var(--color-text-secondary)">
                    <th class="text-left py-2">분류</th>
                    <th class="text-right py-2">목표</th>
                    <th class="text-right py-2">현재</th>
                    <th class="text-right py-2">차이</th>
                    <th class="text-right py-2">현재 가치</th>
                    <th class="text-right py-2">조정 금액</th>
                    <th class="text-right py-2">상태</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="item in rebalanceSuggestion.items"
                    :key="item.sub_category"
                    class="border-t"
                    style="border-color: var(--color-border)"
                  >
                    <td class="py-3">
                      <div class="font-medium">{{ item.label }}</div>
                      <div class="text-xs" style="color: var(--color-text-secondary)">
                        {{ item.category }}
                      </div>
                    </td>
                    <td class="text-right py-3">{{ item.target_pct }}%</td>
                    <td class="text-right py-3">{{ item.current_pct }}%</td>
                    <td
                      class="text-right py-3 font-medium"
                      :class="{
                        'text-red-400': item.diff_pct > 0 && Math.abs(item.diff_pct) >= rebalanceThreshold,
                        'text-green-400': item.diff_pct < 0 && Math.abs(item.diff_pct) >= rebalanceThreshold,
                        '': Math.abs(item.diff_pct) < rebalanceThreshold,
                      }"
                    >
                      {{ item.diff_pct >= 0 ? '+' : '' }}{{ item.diff_pct }}%
                    </td>
                    <td class="text-right py-3">{{ formatKRW(item.current_value) }}</td>
                    <td
                      class="text-right py-3"
                      :class="item.adjust_amount > 0 ? 'text-green-400' : item.adjust_amount < 0 ? 'text-red-400' : ''"
                    >
                      {{ item.adjust_amount > 0 ? '+' : '' }}{{ formatKRW(item.adjust_amount) }}
                    </td>
                    <td class="text-right py-3">
                      <span
                        class="text-xs px-2 py-0.5 rounded"
                        :class="{
                          'bg-green-500/20 text-green-400': item.action === '매수 필요',
                          'bg-red-500/20 text-red-400': item.action === '매도 필요',
                          'bg-gray-500/20 text-gray-400': item.action === '유지',
                        }"
                      >
                        {{ item.action }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- 목표 배분 목록 -->
            <div class="rounded-lg p-4" style="background-color: var(--color-bg-secondary)">
              <h3 class="text-sm font-semibold mb-3">현재 목표 배분 설정</h3>
              <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
                <div
                  v-for="target in targets"
                  :key="target.id"
                  class="flex items-center justify-between px-3 py-2 rounded"
                  style="background-color: var(--color-bg-tertiary)"
                >
                  <div>
                    <span class="text-sm">{{ target.label || target.sub_category }}</span>
                    <span class="text-xs ml-1" style="color: var(--color-text-secondary)">({{ target.category }})</span>
                  </div>
                  <span class="text-sm font-semibold">{{ target.target_pct }}%</span>
                </div>
              </div>
            </div>
          </template>
        </template>
      </template>
    </template>
  </div>
</template>
