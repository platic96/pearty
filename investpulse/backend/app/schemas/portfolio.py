"""포트폴리오 + 리밸런싱 Pydantic 스키마."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, field_validator


AssetType = Literal["crypto", "stock", "cash_bond"]


class PortfolioAssetCreate(BaseModel):
    symbol: str
    asset_type: AssetType = "crypto"
    name: str = ""
    quantity: float
    avg_buy_price: float
    asset_class: str = ""

    @field_validator("quantity")
    @classmethod
    def quantity_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("수량은 0보다 커야 합니다")
        return v

    @field_validator("avg_buy_price")
    @classmethod
    def price_non_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("평균 매수가는 0 이상이어야 합니다")
        return v


class PortfolioAssetUpdate(BaseModel):
    quantity: float | None = None
    avg_buy_price: float | None = None
    name: str | None = None
    asset_class: str | None = None


class PortfolioAssetResponse(BaseModel):
    id: int
    symbol: str
    asset_type: str
    name: str
    quantity: float
    avg_buy_price: float
    asset_class: str
    current_price: float | None = None
    profit_loss: float | None = None
    profit_loss_pct: float | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AssetGroupSummary(BaseModel):
    """자산군별 요약."""
    asset_type: str
    label: str
    total_invested: float
    total_current_value: float
    profit_loss: float
    profit_loss_pct: float
    weight_pct: float  # 전체 대비 현재 비중 %
    assets: list[PortfolioAssetResponse]


class PortfolioSummary(BaseModel):
    total_invested: float
    total_current_value: float
    total_profit_loss: float
    total_profit_loss_pct: float
    assets: list[PortfolioAssetResponse]
    groups: list[AssetGroupSummary] = []


# ── 목표 배분 ───────────────────────────────────

class TargetAllocationCreate(BaseModel):
    category: str  # stocks, crypto, cash_bonds
    sub_category: str = ""
    label: str = ""
    target_pct: float

    @field_validator("target_pct")
    @classmethod
    def pct_range(cls, v: float) -> float:
        if v < 0 or v > 100:
            raise ValueError("목표 비중은 0~100 사이여야 합니다")
        return v


class TargetAllocationUpdate(BaseModel):
    label: str | None = None
    target_pct: float | None = None

    @field_validator("target_pct")
    @classmethod
    def pct_range(cls, v: float | None) -> float | None:
        if v is not None and (v < 0 or v > 100):
            raise ValueError("목표 비중은 0~100 사이여야 합니다")
        return v


class TargetAllocationResponse(BaseModel):
    id: int
    category: str
    sub_category: str
    label: str
    target_pct: float
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── 리밸런싱 ────────────────────────────────────

class RebalanceItem(BaseModel):
    """리밸런싱 개별 항목."""
    category: str
    sub_category: str
    label: str
    target_pct: float
    current_pct: float
    diff_pct: float  # current - target (양수=초과, 음수=부족)
    current_value: float
    target_value: float
    action: str  # "매수 필요", "매도 필요", "유지"
    adjust_amount: float  # 조정 필요 금액 (양수=매수, 음수=매도)


class RebalanceSuggestion(BaseModel):
    """리밸런싱 제안 결과."""
    total_portfolio_value: float
    rebalance_threshold_pct: float
    needs_rebalance: bool
    items: list[RebalanceItem]
    summary: str  # 사람이 읽을 수 있는 요약
