<script setup lang="ts">
import { useUiStore } from '@/stores/ui'
import { storeToRefs } from 'pinia'
import { LayoutDashboard, Bell, Wallet, TrendingUp, ChevronLeft, ChevronRight } from 'lucide-vue-next'
import { DEFAULT_MARKETS } from '@/utils/constants'

const uiStore = useUiStore()
const { selectedMarket, selectedTimeframe, sidebarOpen, timeframes } = storeToRefs(uiStore)
</script>

<template>
  <aside
    class="h-screen flex flex-col border-r transition-all duration-300"
    :class="sidebarOpen ? 'w-60' : 'w-16'"
    style="background-color: var(--color-bg-secondary); border-color: var(--color-border)"
  >
    <!-- Header -->
    <div class="flex items-center justify-between p-4">
      <h1 v-if="sidebarOpen" class="text-lg font-bold" style="color: var(--color-accent)">
        InvestPulse
      </h1>
      <button
        class="p-1 rounded hover:bg-white/10"
        @click="uiStore.toggleSidebar()"
      >
        <ChevronLeft v-if="sidebarOpen" :size="18" />
        <ChevronRight v-else :size="18" />
      </button>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 px-2 space-y-1">
      <router-link
        to="/"
        class="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-white/10 transition-colors"
        active-class="!bg-indigo-500/20 text-indigo-400"
      >
        <LayoutDashboard :size="20" />
        <span v-if="sidebarOpen">Dashboard</span>
      </router-link>
      <router-link
        to="/alerts"
        class="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-white/10 transition-colors"
        active-class="!bg-indigo-500/20 text-indigo-400"
      >
        <Bell :size="20" />
        <span v-if="sidebarOpen">Alerts</span>
      </router-link>
      <router-link
        to="/stocks"
        class="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-white/10 transition-colors"
        active-class="!bg-indigo-500/20 text-indigo-400"
      >
        <TrendingUp :size="20" />
        <span v-if="sidebarOpen">Stocks</span>
      </router-link>
      <router-link
        to="/portfolio"
        class="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-white/10 transition-colors"
        active-class="!bg-indigo-500/20 text-indigo-400"
      >
        <Wallet :size="20" />
        <span v-if="sidebarOpen">Portfolio</span>
      </router-link>
    </nav>

    <!-- Market / Timeframe selectors -->
    <div v-if="sidebarOpen" class="p-4 space-y-3 border-t" style="border-color: var(--color-border)">
      <div>
        <label class="text-xs uppercase tracking-wider" style="color: var(--color-text-secondary)">Market</label>
        <select
          v-model="selectedMarket"
          class="mt-1 w-full rounded px-2 py-1.5 text-sm"
          style="background-color: var(--color-bg-tertiary); border: 1px solid var(--color-border); color: var(--color-text-primary)"
        >
          <option v-for="m in DEFAULT_MARKETS" :key="m" :value="m">{{ m }}</option>
        </select>
      </div>
      <div>
        <label class="text-xs uppercase tracking-wider" style="color: var(--color-text-secondary)">Timeframe</label>
        <div class="mt-1 flex flex-wrap gap-1">
          <button
            v-for="tf in timeframes"
            :key="tf"
            class="px-2 py-1 text-xs rounded transition-colors"
            :class="selectedTimeframe === tf ? 'bg-indigo-500 text-white' : 'hover:bg-white/10'"
            style="border: 1px solid var(--color-border)"
            @click="uiStore.setTimeframe(tf)"
          >
            {{ tf }}
          </button>
        </div>
      </div>
    </div>
  </aside>
</template>
