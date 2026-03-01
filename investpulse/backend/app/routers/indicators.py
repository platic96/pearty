from fastapi import APIRouter, Depends, Query

from app.routers.market import get_upbit_service
from app.schemas.market import IndicatorResponse
from app.services.indicators import IndicatorService
from app.services.upbit import UpbitService

router = APIRouter(prefix="/api/indicators", tags=["indicators"])


@router.get("/{symbol}", response_model=IndicatorResponse)
async def get_indicators(
    symbol: str,
    timeframe: str = Query(default="1d"),
    upbit: UpbitService = Depends(get_upbit_service),
):
    """기술지표(RSI, MACD, Bollinger Bands) 전체 조회."""
    market = f"KRW-{symbol.upper()}"
    candles = await upbit.get_candles(market, timeframe, 200)
    result = IndicatorService.calculate_all(candles)
    return IndicatorResponse(**result)


@router.get("/{symbol}/history")
async def get_indicator_history(
    symbol: str,
    indicator: str = Query(default="RSI"),
    timeframe: str = Query(default="1d"),
    upbit: UpbitService = Depends(get_upbit_service),
):
    """개별 지표 시계열 데이터 조회."""
    market = f"KRW-{symbol.upper()}"
    candles = await upbit.get_candles(market, timeframe, 200)
    result = IndicatorService.calculate_all(candles)

    indicator_key = indicator.lower()
    key_map = {"rsi": "rsi", "macd": "macd", "bb": "bollinger_bands"}
    data_key = key_map.get(indicator_key, "rsi")

    return {
        "indicator": indicator,
        "timeframe": timeframe,
        "data": result.get(data_key, {}),
        "timestamps": result["timestamps"],
    }
