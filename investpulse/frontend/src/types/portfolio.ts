export interface PortfolioAsset {
  id: number
  symbol: string
  asset_type: string
  quantity: number
  avg_buy_price: number
  current_price: number | null
  profit_loss: number | null
  profit_loss_pct: number | null
  created_at: string
  updated_at: string
}

export interface PortfolioSummary {
  total_invested: number
  total_current_value: number
  total_profit_loss: number
  total_profit_loss_pct: number
  assets: PortfolioAsset[]
}

export interface PortfolioAssetCreate {
  symbol: string
  asset_type: string
  quantity: number
  avg_buy_price: number
}
