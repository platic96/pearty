from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class PortfolioAsset(Base):
    __tablename__ = "portfolio_assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String, index=True)
    asset_type: Mapped[str] = mapped_column(String, default="crypto")  # crypto, stock, cash_bond
    name: Mapped[str] = mapped_column(String, default="")  # 종목명
    quantity: Mapped[float] = mapped_column(Float)
    avg_buy_price: Mapped[float] = mapped_column(Float)
    asset_class: Mapped[str] = mapped_column(String, default="")  # 세부 분류 (us_growth, btc, domestic_dividend 등)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class TargetAllocation(Base):
    """목표 자산배분 비중 — 리밸런싱 기준."""
    __tablename__ = "target_allocations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category: Mapped[str] = mapped_column(String, index=True)  # stocks, crypto, cash_bonds
    sub_category: Mapped[str] = mapped_column(String, default="")  # us_growth_tech, btc, etc.
    label: Mapped[str] = mapped_column(String, default="")  # 사용자 표시명
    target_pct: Mapped[float] = mapped_column(Float)  # 전체 포트폴리오 대비 목표 %
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
