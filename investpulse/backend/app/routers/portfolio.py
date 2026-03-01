from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models.portfolio import PortfolioAsset
from app.routers.market import get_upbit_service
from app.schemas.portfolio import (
    PortfolioAssetCreate,
    PortfolioAssetResponse,
    PortfolioAssetUpdate,
    PortfolioSummary,
)
from app.services.upbit import UpbitService

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])


@router.get("", response_model=PortfolioSummary)
async def get_portfolio(
    session: AsyncSession = Depends(get_session),
    upbit: UpbitService = Depends(get_upbit_service),
):
    """포트폴리오 요약 조회 (현재가 포함)."""
    result = await session.execute(select(PortfolioAsset))
    assets = result.scalars().all()

    asset_responses = []
    total_invested = 0.0
    total_current = 0.0

    # 마켓 심볼 수집하여 한번에 조회
    crypto_symbols = [a.symbol for a in assets if a.asset_type == "crypto"]
    prices: dict[str, float] = {}

    if crypto_symbols:
        markets = [f"KRW-{s}" for s in crypto_symbols]
        try:
            tickers = await upbit.get_ticker(markets)
            for t in tickers:
                symbol = t["market"].replace("KRW-", "")
                prices[symbol] = t["trade_price"]
        except Exception:
            pass

    for asset in assets:
        current_price = prices.get(asset.symbol)
        invested = asset.quantity * asset.avg_buy_price
        current_value = asset.quantity * current_price if current_price else 0
        profit_loss = current_value - invested if current_price else None
        profit_loss_pct = (profit_loss / invested * 100) if profit_loss is not None and invested > 0 else None

        total_invested += invested
        total_current += current_value

        asset_responses.append(
            PortfolioAssetResponse(
                id=asset.id,
                symbol=asset.symbol,
                asset_type=asset.asset_type,
                quantity=asset.quantity,
                avg_buy_price=asset.avg_buy_price,
                current_price=current_price,
                profit_loss=round(profit_loss, 2) if profit_loss is not None else None,
                profit_loss_pct=round(profit_loss_pct, 2) if profit_loss_pct is not None else None,
                created_at=asset.created_at,
                updated_at=asset.updated_at,
            )
        )

    total_pl = total_current - total_invested
    total_pl_pct = (total_pl / total_invested * 100) if total_invested > 0 else 0

    return PortfolioSummary(
        total_invested=round(total_invested, 2),
        total_current_value=round(total_current, 2),
        total_profit_loss=round(total_pl, 2),
        total_profit_loss_pct=round(total_pl_pct, 2),
        assets=asset_responses,
    )


@router.post("/assets", response_model=PortfolioAssetResponse)
async def add_asset(
    data: PortfolioAssetCreate, session: AsyncSession = Depends(get_session)
):
    """포트폴리오에 자산 추가."""
    asset = PortfolioAsset(
        symbol=data.symbol.upper(),
        asset_type=data.asset_type,
        quantity=data.quantity,
        avg_buy_price=data.avg_buy_price,
    )
    session.add(asset)
    await session.commit()
    await session.refresh(asset)
    return asset


@router.put("/assets/{asset_id}", response_model=PortfolioAssetResponse)
async def update_asset(
    asset_id: int,
    data: PortfolioAssetUpdate,
    session: AsyncSession = Depends(get_session),
):
    """포트폴리오 자산 수정."""
    result = await session.execute(
        select(PortfolioAsset).where(PortfolioAsset.id == asset_id)
    )
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(asset, key, value)

    await session.commit()
    await session.refresh(asset)
    return asset


@router.delete("/assets/{asset_id}")
async def delete_asset(
    asset_id: int, session: AsyncSession = Depends(get_session)
):
    """포트폴리오 자산 삭제."""
    result = await session.execute(
        select(PortfolioAsset).where(PortfolioAsset.id == asset_id)
    )
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    await session.delete(asset)
    await session.commit()
    return {"status": "deleted", "id": asset_id}
