from datetime import datetime

from pydantic import BaseModel


class CandleResponse(BaseModel):
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float


class TickerResponse(BaseModel):
    market: str
    trade_price: float
    signed_change_rate: float
    acc_trade_volume_24h: float
    high_price: float
    low_price: float
    timestamp: int


class MarketInfo(BaseModel):
    market: str
    korean_name: str
    english_name: str


class IndicatorResponse(BaseModel):
    rsi: dict
    macd: dict
    bollinger_bands: dict
    timestamps: list[str]
