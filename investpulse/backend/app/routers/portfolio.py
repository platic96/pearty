"""포트폴리오 CRUD + 자산군별 그룹 요약 라우터."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models.portfolio import PortfolioAsset
from app.routers.market import get_upbit_service
from app.routers.stocks import get_kis_service
from app.schemas.portfolio import (
    AssetGroupSummary,
    PortfolioAssetCreate,
    PortfolioAssetResponse,
    PortfolioAssetUpdate,
    PortfolioSummary,
)
from app.services.kis import KISService
from app.services.upbit import UpbitService

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])

ASSET_TYPE_LABELS = {
    "crypto": "암호화폐",
    "stock": "주식",
    "cash_bond": "현금/채권",
}


@router.get("", response_model=PortfolioSummary)
async def get_portfolio(
    session: AsyncSession = Depends(get_session),
    upbit: UpbitService = Depends(get_upbit_service),
    kis: KISService = Depends(get_kis_service),
):
    """포트폴리오 요약 조회 (현재가 포함, 자산군별 그룹)."""
    result = await session.execute(select(PortfolioAsset))
    assets = result.scalars().all()

    # ── 현재가 조회 ──
    prices: dict[str, float] = {}

    # 암호화폐
    crypto_symbols = [a.symbol for a in assets if a.asset_type == "crypto"]
    if crypto_symbols:
        markets = [f"KRW-{s}" for s in crypto_symbols]
        try:
            tickers = await upbit.get_ticker(markets)
            for t in tickers:
                symbol = t["market"].replace("KRW-", "")
                prices[symbol] = t["trade_price"]
        except Exception:
            pass

    # 주식
    stock_codes = [a.symbol for a in assets if a.asset_type == "stock"]
    if stock_codes and kis.is_configured():
        try:
            stock_prices = await kis.get_stock_prices_batch(stock_codes)
            for sp in stock_prices:
                prices[sp["stock_code"]] = sp["price"]
        except Exception:
            pass

    # ── 자산 응답 + 그룹 계산 ──
    asset_responses: list[PortfolioAssetResponse] = []
    total_invested = 0.0
    total_current = 0.0

    # 그룹별 집계
    group_data: dict[str, dict] = {}

    for asset in assets:
        if asset.asset_type == "cash_bond":
            current_price = asset.avg_buy_price  # 현금/채권은 액면가 유지
        else:
            current_price = prices.get(asset.symbol)

        invested = asset.quantity * asset.avg_buy_price
        current_value = asset.quantity * current_price if current_price else 0
        profit_loss = current_value - invested if current_price else None
        profit_loss_pct = (profit_loss / invested * 100) if profit_loss is not None and invested > 0 else None

        total_invested += invested
        total_current += current_value

        resp = PortfolioAssetResponse(
            id=asset.id,
            symbol=asset.symbol,
            asset_type=asset.asset_type,
            name=asset.name or asset.symbol,
            quantity=asset.quantity,
            avg_buy_price=asset.avg_buy_price,
            asset_class=asset.asset_class or "",
            current_price=current_price,
            profit_loss=round(profit_loss, 2) if profit_loss is not None else None,
            profit_loss_pct=round(profit_loss_pct, 2) if profit_loss_pct is not None else None,
            created_at=asset.created_at,
            updated_at=asset.updated_at,
        )
        asset_responses.append(resp)

        # 그룹 집계
        at = asset.asset_type
        if at not in group_data:
            group_data[at] = {"invested": 0.0, "current": 0.0, "assets": []}
        group_data[at]["invested"] += invested
        group_data[at]["current"] += current_value
        group_data[at]["assets"].append(resp)

    # ── 그룹 요약 ──
    groups: list[AssetGroupSummary] = []
    for at, gd in group_data.items():
        g_invested = gd["invested"]
        g_current = gd["current"]
        g_pl = g_current - g_invested
        g_pl_pct = (g_pl / g_invested * 100) if g_invested > 0 else 0
        weight_pct = (g_current / total_current * 100) if total_current > 0 else 0

        groups.append(
            AssetGroupSummary(
                asset_type=at,
                label=ASSET_TYPE_LABELS.get(at, at),
                total_invested=round(g_invested, 2),
                total_current_value=round(g_current, 2),
                profit_loss=round(g_pl, 2),
                profit_loss_pct=round(g_pl_pct, 2),
                weight_pct=round(weight_pct, 2),
                assets=gd["assets"],
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
        groups=groups,
    )


@router.post("/assets", response_model=PortfolioAssetResponse)
async def add_asset(
    data: PortfolioAssetCreate, session: AsyncSession = Depends(get_session)
):
    """포트폴리오에 자산 추가."""
    asset = PortfolioAsset(
        symbol=data.symbol.upper(),
        asset_type=data.asset_type,
        name=data.name,
        quantity=data.quantity,
        avg_buy_price=data.avg_buy_price,
        asset_class=data.asset_class,
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
