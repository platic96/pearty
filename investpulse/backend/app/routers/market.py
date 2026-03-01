from fastapi import APIRouter, Depends, Query

from app.schemas.market import CandleResponse, MarketInfo, TickerResponse
from app.services.upbit import UpbitService

router = APIRouter(prefix="/api/market", tags=["market"])


def get_upbit_service() -> UpbitService:
    return _upbit_service


_upbit_service = UpbitService()


@router.get("/markets", response_model=list[MarketInfo])
async def get_markets(upbit: UpbitService = Depends(get_upbit_service)):
    """KRW 마켓 전체 목록 조회."""
    markets = await upbit.get_markets()
    return [
        MarketInfo(
            market=m["market"],
            korean_name=m["korean_name"],
            english_name=m["english_name"],
        )
        for m in markets
    ]


@router.get("/crypto/{symbol}", response_model=TickerResponse)
async def get_crypto_price(
    symbol: str, upbit: UpbitService = Depends(get_upbit_service)
):
    """암호화폐 현재가 조회. symbol 예: BTC, ETH"""
    market = f"KRW-{symbol.upper()}"
    tickers = await upbit.get_ticker([market])
    t = tickers[0]
    return TickerResponse(
        market=t["market"],
        trade_price=t["trade_price"],
        signed_change_rate=t["signed_change_rate"],
        acc_trade_volume_24h=t["acc_trade_volume_24h"],
        high_price=t["high_price"],
        low_price=t["low_price"],
        timestamp=t["timestamp"],
    )


@router.get("/candles/{symbol}", response_model=list[CandleResponse])
async def get_candles(
    symbol: str,
    timeframe: str = Query(default="1d"),
    count: int = Query(default=200, le=200),
    upbit: UpbitService = Depends(get_upbit_service),
):
    """캔들(OHLCV) 데이터 조회."""
    market = f"KRW-{symbol.upper()}"
    candles = await upbit.get_candles(market, timeframe, count)
    return [CandleResponse(**c) for c in candles]
