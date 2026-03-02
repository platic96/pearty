export type AssetType = 'crypto' | 'stock' | 'cash_bond'

export interface PortfolioAsset {
  id: number
  symbol: string
  asset_type: AssetType
  name: string
  quantity: number
  avg_buy_price: number
  asset_class: string
  current_price: number | null
  profit_loss: number | null
  profit_loss_pct: number | null
  created_at: string
  updated_at: string
}

export interface AssetGroupSummary {
  asset_type: string
  label: string
  total_invested: number
  total_current_value: number
  profit_loss: number
  profit_loss_pct: number
  weight_pct: number
  assets: PortfolioAsset[]
}

export interface PortfolioSummary {
  total_invested: number
  total_current_value: number
  total_profit_loss: number
  total_profit_loss_pct: number
  assets: PortfolioAsset[]
  groups: AssetGroupSummary[]
}

export interface PortfolioAssetCreate {
  symbol: string
  asset_type: AssetType
  name?: string
  quantity: number
  avg_buy_price: number
  asset_class?: string
}
