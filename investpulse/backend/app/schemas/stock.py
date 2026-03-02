"""주식 관련 Pydantic 스키마."""

from pydantic import BaseModel


class StockPriceResponse(BaseModel):
    stock_code: str
    name: str
    price: int
    change: int
    change_pct: float
    volume: int
    market_cap: int
    high: int
    low: int
    open: int
    prev_close: int


class StockSearchResult(BaseModel):
    stock_code: str
    name: str


class StockCandleResponse(BaseModel):
    timestamp: str
    open: int
    high: int
    low: int
    close: int
    volume: int
