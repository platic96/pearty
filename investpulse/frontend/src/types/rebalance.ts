export interface TargetAllocation {
  id: number
  category: string
  sub_category: string
  label: string
  target_pct: number
  created_at: string
  updated_at: string
}

export interface TargetAllocationCreate {
  category: string
  sub_category: string
  label: string
  target_pct: number
}

export interface TargetAllocationUpdate {
  label?: string
  target_pct?: number
}

export interface RebalanceItem {
  category: string
  sub_category: string
  label: string
  target_pct: number
  current_pct: number
  diff_pct: number
  current_value: number
  target_value: number
  action: string
  adjust_amount: number
}

export interface RebalanceSuggestion {
  total_portfolio_value: number
  rebalance_threshold_pct: number
  needs_rebalance: boolean
  items: RebalanceItem[]
  summary: string
}
