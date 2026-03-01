from datetime import datetime

from pydantic import BaseModel


class PortfolioAssetCreate(BaseModel):
    symbol: str
    asset_type: str = "crypto"
    quantity: float
    avg_buy_price: float


class PortfolioAssetUpdate(BaseModel):
    quantity: float | None = None
    avg_buy_price: float | None = None


class PortfolioAssetResponse(BaseModel):
    id: int
    symbol: str
    asset_type: str
    quantity: float
    avg_buy_price: float
    current_price: float | None = None
    profit_loss: float | None = None
    profit_loss_pct: float | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PortfolioSummary(BaseModel):
    total_invested: float
    total_current_value: float
    total_profit_loss: float
    total_profit_loss_pct: float
    assets: list[PortfolioAssetResponse]
