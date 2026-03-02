"""리밸런싱 + 목표 배분 관리 라우터."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models.portfolio import PortfolioAsset, TargetAllocation
from app.routers.market import get_upbit_service
from app.routers.stocks import get_kis_service
from app.schemas.portfolio import (
    RebalanceSuggestion,
    TargetAllocationCreate,
    TargetAllocationResponse,
    TargetAllocationUpdate,
)
from app.services.kis import KISService
from app.services.rebalance import DEFAULT_TARGET_ALLOCATIONS, RebalanceService
from app.services.upbit import UpbitService

router = APIRouter(prefix="/api/rebalance", tags=["rebalance"])

_rebalance_service = RebalanceService()


# ── 목표 배분 CRUD ──────────────────────────────

@router.get("/targets", response_model=list[TargetAllocationResponse])
async def get_targets(session: AsyncSession = Depends(get_session)):
    """목표 자산배분 조회."""
    result = await session.execute(
        select(TargetAllocation).order_by(TargetAllocation.category, TargetAllocation.target_pct.desc())
    )
    return result.scalars().all()


@router.post("/targets", response_model=TargetAllocationResponse)
async def create_target(
    data: TargetAllocationCreate,
    session: AsyncSession = Depends(get_session),
):
    """목표 배분 항목 추가."""
    target = TargetAllocation(
        category=data.category,
        sub_category=data.sub_category,
        label=data.label,
        target_pct=data.target_pct,
    )
    session.add(target)
    await session.commit()
    await session.refresh(target)
    return target


@router.put("/targets/{target_id}", response_model=TargetAllocationResponse)
async def update_target(
    target_id: int,
    data: TargetAllocationUpdate,
    session: AsyncSession = Depends(get_session),
):
    """목표 배분 항목 수정."""
    result = await session.execute(
        select(TargetAllocation).where(TargetAllocation.id == target_id)
    )
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="목표 배분 항목을 찾을 수 없습니다")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(target, key, value)

    await session.commit()
    await session.refresh(target)
    return target


@router.delete("/targets/{target_id}")
async def delete_target(
    target_id: int,
    session: AsyncSession = Depends(get_session),
):
    """목표 배분 항목 삭제."""
    result = await session.execute(
        select(TargetAllocation).where(TargetAllocation.id == target_id)
    )
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="목표 배분 항목을 찾을 수 없습니다")

    await session.delete(target)
    await session.commit()
    return {"status": "deleted", "id": target_id}


@router.post("/targets/init-defaults")
async def init_default_targets(session: AsyncSession = Depends(get_session)):
    """기본 목표 배분을 초기화 (개인 전략 템플릿 기반).

    이미 데이터가 있으면 스킵합니다.
    """
    existing = await session.execute(select(TargetAllocation))
    if existing.scalars().first():
        return {"status": "skipped", "message": "이미 목표 배분이 설정되어 있습니다"}

    for item in DEFAULT_TARGET_ALLOCATIONS:
        session.add(TargetAllocation(**item))
    await session.commit()
    return {"status": "initialized", "count": len(DEFAULT_TARGET_ALLOCATIONS)}


# ── 리밸런싱 계산 ────────────────────────────────

@router.get("/suggest", response_model=RebalanceSuggestion)
async def suggest_rebalance(
    threshold: float = Query(5.0, ge=1.0, le=20.0, description="리밸런싱 트리거 기준 (%)"),
    session: AsyncSession = Depends(get_session),
    upbit: UpbitService = Depends(get_upbit_service),
    kis: KISService = Depends(get_kis_service),
):
    """현재 포트폴리오와 목표 배분을 비교하여 리밸런싱 제안 생성."""
    # 1. 목표 배분 조회
    target_result = await session.execute(
        select(TargetAllocation).order_by(TargetAllocation.category)
    )
    targets = target_result.scalars().all()
    if not targets:
        raise HTTPException(status_code=400, detail="목표 배분이 설정되지 않았습니다. POST /api/rebalance/targets/init-defaults를 먼저 실행하세요.")

    # 2. 포트폴리오 자산 조회
    asset_result = await session.execute(select(PortfolioAsset))
    assets = asset_result.scalars().all()

    # 3. 현재 가격 조회 (crypto + stock)
    crypto_assets = [a for a in assets if a.asset_type == "crypto"]
    stock_assets = [a for a in assets if a.asset_type == "stock"]
    cash_assets = [a for a in assets if a.asset_type == "cash_bond"]

    prices: dict[str, float] = {}

    # 3a. 암호화폐 가격
    if crypto_assets:
        markets = [f"KRW-{a.symbol}" for a in crypto_assets]
        try:
            tickers = await upbit.get_ticker(markets)
            for t in tickers:
                symbol = t["market"].replace("KRW-", "")
                prices[symbol] = t["trade_price"]
        except Exception:
            pass

    # 3b. 주식 가격
    if stock_assets and kis.is_configured():
        try:
            stock_prices = await kis.get_stock_prices_batch([a.symbol for a in stock_assets])
            for sp in stock_prices:
                prices[sp["stock_code"]] = sp["price"]
        except Exception:
            pass

    # 4. sub_category별 현재 가치 계산
    current_values: dict[str, float] = {}

    for asset in crypto_assets:
        price = prices.get(asset.symbol, asset.avg_buy_price)
        value = asset.quantity * price
        sub_cat = asset.asset_class or _infer_crypto_sub_category(asset.symbol)
        current_values[sub_cat] = current_values.get(sub_cat, 0) + value

    for asset in stock_assets:
        price = prices.get(asset.symbol, asset.avg_buy_price)
        value = asset.quantity * price
        sub_cat = asset.asset_class or "domestic_growth"
        current_values[sub_cat] = current_values.get(sub_cat, 0) + value

    for asset in cash_assets:
        value = asset.quantity * asset.avg_buy_price
        current_values["cash_bonds"] = current_values.get("cash_bonds", 0) + value

    total_portfolio_value = sum(current_values.values())

    # 5. 리밸런싱 계산
    target_dicts = [
        {
            "category": t.category,
            "sub_category": t.sub_category,
            "label": t.label,
            "target_pct": t.target_pct,
        }
        for t in targets
    ]

    return _rebalance_service.calculate(
        targets=target_dicts,
        current_values=current_values,
        total_portfolio_value=total_portfolio_value,
        threshold_pct=threshold,
    )


def _infer_crypto_sub_category(symbol: str) -> str:
    """심볼로부터 암호화폐 세부 분류를 추론."""
    symbol_upper = symbol.upper()
    if symbol_upper == "BTC":
        return "btc"
    elif symbol_upper == "ETH":
        return "eth"
    else:
        return "altcoins"
