import asyncio

import httpx

from app.config import settings


class UpbitService:
    """Upbit REST API 래퍼 — KRW 마켓 암호화폐 데이터 조회."""

    CANDLE_ENDPOINT_MAP = {
        "1m": "/candles/minutes/1",
        "3m": "/candles/minutes/3",
        "5m": "/candles/minutes/5",
        "15m": "/candles/minutes/15",
        "30m": "/candles/minutes/30",
        "1h": "/candles/minutes/60",
        "4h": "/candles/minutes/240",
        "1d": "/candles/days",
        "1w": "/candles/weeks",
        "1M": "/candles/months",
    }

    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None
        self._semaphore = asyncio.Semaphore(8)

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=settings.UPBIT_API_BASE_URL,
                timeout=10.0,
                headers={"accept": "application/json"},
            )
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def get_markets(self) -> list[dict]:
        """KRW 마켓 목록 조회."""
        async with self._semaphore:
            client = await self._get_client()
            resp = await client.get("/market/all")
            resp.raise_for_status()
        return [m for m in resp.json() if m["market"].startswith("KRW-")]

    async def get_ticker(self, markets: list[str]) -> list[dict]:
        """현재가(ticker) 조회."""
        async with self._semaphore:
            client = await self._get_client()
            resp = await client.get("/ticker", params={"markets": ",".join(markets)})
            resp.raise_for_status()
        return resp.json()

    async def get_candles(
        self,
        market: str,
        timeframe: str = "1d",
        count: int = 200,
        to: str | None = None,
    ) -> list[dict]:
        """캔들 데이터 조회 후 정규화된 형태로 반환.

        Returns:
            시간순 정렬된 캔들 리스트. 각 항목: timestamp, open, high, low, close, volume
        """
        endpoint = self.CANDLE_ENDPOINT_MAP.get(timeframe, "/candles/days")
        params: dict = {"market": market, "count": min(count, 200)}
        if to:
            params["to"] = to

        async with self._semaphore:
            client = await self._get_client()
            resp = await client.get(endpoint, params=params)
            resp.raise_for_status()

        raw = resp.json()
        # Upbit 응답은 최신→과거 순이므로 reverse하여 시간순 정렬
        return [self._normalize_candle(c) for c in reversed(raw)]

    @staticmethod
    def _normalize_candle(raw: dict) -> dict:
        """Upbit 캔들 응답을 표준 OHLCV 형태로 변환."""
        return {
            "timestamp": raw["candle_date_time_utc"],
            "open": raw["opening_price"],
            "high": raw["high_price"],
            "low": raw["low_price"],
            "close": raw["trade_price"],
            "volume": raw["candle_acc_trade_volume"],
        }
