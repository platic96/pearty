"""한국투자증권 OpenAPI 서비스 — 주식 시세, 캔들, 종목 조회."""

import asyncio
import time

import httpx

from app.config import settings


class KISService:
    """한국투자증권 OpenAPI 래퍼.

    - OAuth2 토큰 자동 관리 (만료 시 갱신)
    - 국내 주식 현재가, 일/주/월봉 조회
    - 종목 마스터(이름/시장구분) 조회
    """

    TOKEN_EXPIRE_BUFFER = 300  # 만료 5분 전 갱신

    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None
        self._semaphore = asyncio.Semaphore(5)
        self._access_token: str = ""
        self._token_expires_at: float = 0.0

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=settings.KIS_BASE_URL,
                timeout=15.0,
            )
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    def is_configured(self) -> bool:
        """API 키가 설정되어 있는지 확인."""
        return bool(settings.KIS_APP_KEY and settings.KIS_APP_SECRET)

    # ── 인증 ──────────────────────────────────────────

    async def _ensure_token(self) -> str:
        """유효한 액세스 토큰 반환. 만료 시 자동 갱신."""
        if self._access_token and time.time() < self._token_expires_at - self.TOKEN_EXPIRE_BUFFER:
            return self._access_token

        client = await self._get_client()
        resp = await client.post(
            "/oauth2/tokenP",
            json={
                "grant_type": "client_credentials",
                "appkey": settings.KIS_APP_KEY,
                "appsecret": settings.KIS_APP_SECRET,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        self._access_token = data["access_token"]
        # KIS 토큰 유효기간: 약 24시간 (86400초)
        self._token_expires_at = time.time() + data.get("expires_in", 86400)
        return self._access_token

    def _common_headers(self, token: str, tr_id: str) -> dict:
        return {
            "authorization": f"Bearer {token}",
            "appkey": settings.KIS_APP_KEY,
            "appsecret": settings.KIS_APP_SECRET,
            "tr_id": tr_id,
            "content-type": "application/json; charset=utf-8",
        }

    # ── 주식 현재가 ──────────────────────────────────

    async def get_stock_price(self, stock_code: str) -> dict:
        """국내 주식 현재가 조회.

        Args:
            stock_code: 종목코드 6자리 (예: "005930" 삼성전자)

        Returns:
            {stock_code, name, price, change, change_pct, volume,
             market_cap, high, low, open, prev_close}
        """
        token = await self._ensure_token()
        tr_id = "FHKST01010100"  # 주식현재가 시세

        async with self._semaphore:
            client = await self._get_client()
            resp = await client.get(
                "/uapi/domestic-stock/v1/quotations/inquire-price",
                headers=self._common_headers(token, tr_id),
                params={
                    "FID_COND_MRKT_DIV_CODE": "J",  # J=주식
                    "FID_INPUT_ISCD": stock_code,
                },
            )
            resp.raise_for_status()

        data = resp.json()
        output = data.get("output", {})

        return {
            "stock_code": stock_code,
            "name": output.get("hts_kor_isnm", ""),
            "price": int(output.get("stck_prpr", 0)),
            "change": int(output.get("prdy_vrss", 0)),
            "change_pct": float(output.get("prdy_ctrt", 0)),
            "volume": int(output.get("acml_vol", 0)),
            "market_cap": int(output.get("hts_avls", 0)),
            "high": int(output.get("stck_hgpr", 0)),
            "low": int(output.get("stck_lwpr", 0)),
            "open": int(output.get("stck_oprc", 0)),
            "prev_close": int(output.get("stck_sdpr", 0)),
        }

    async def get_stock_prices_batch(self, stock_codes: list[str]) -> list[dict]:
        """여러 종목의 현재가를 동시 조회."""
        tasks = [self.get_stock_price(code) for code in stock_codes]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [r for r in results if isinstance(r, dict)]

    # ── 주식 일봉 / 주봉 / 월봉 ──────────────────────

    async def get_stock_candles(
        self,
        stock_code: str,
        period: str = "D",
        count: int = 100,
        end_date: str = "",
        start_date: str = "",
    ) -> list[dict]:
        """국내 주식 기간별 시세 (일/주/월봉) 조회.

        Args:
            stock_code: 종목코드 6자리
            period: D=일봉, W=주봉, M=월봉
            count: 최대 조회 건수
            end_date: 조회 종료일 (YYYYMMDD). 빈 문자열이면 오늘
            start_date: 조회 시작일 (YYYYMMDD). 빈 문자열이면 end_date - count 영업일

        Returns:
            시간순 정렬된 캔들 리스트.
            [{timestamp, open, high, low, close, volume}, ...]
        """
        token = await self._ensure_token()
        tr_id = "FHKST03010100"  # 주식 기간별 시세

        # 날짜 기본값: 오늘
        if not end_date:
            from datetime import datetime
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = "20200101"

        async with self._semaphore:
            client = await self._get_client()
            resp = await client.get(
                "/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice",
                headers=self._common_headers(token, tr_id),
                params={
                    "FID_COND_MRKT_DIV_CODE": "J",
                    "FID_INPUT_ISCD": stock_code,
                    "FID_INPUT_DATE_1": start_date,
                    "FID_INPUT_DATE_2": end_date,
                    "FID_PERIOD_DIV_CODE": period,
                    "FID_ORG_ADJ_PRC": "0",  # 수정주가 반영
                },
            )
            resp.raise_for_status()

        data = resp.json()
        raw_list = data.get("output2", [])

        candles = []
        for raw in raw_list:
            if not raw.get("stck_bsop_date"):
                continue
            candles.append(self._normalize_stock_candle(raw))

        # API 응답은 최신→과거 순이므로 시간순 정렬
        candles.reverse()
        return candles[:count]

    @staticmethod
    def _normalize_stock_candle(raw: dict) -> dict:
        """KIS 주식 캔들 응답을 표준 OHLCV 형태로 변환."""
        date_str = raw.get("stck_bsop_date", "")
        # YYYYMMDD -> YYYY-MM-DD 형태로 변환
        timestamp = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
        return {
            "timestamp": timestamp,
            "open": int(raw.get("stck_oprc", 0)),
            "high": int(raw.get("stck_hgpr", 0)),
            "low": int(raw.get("stck_lwpr", 0)),
            "close": int(raw.get("stck_clpr", 0)),
            "volume": int(raw.get("acml_vol", 0)),
        }

    # ── 인기 / 주요 종목 목록 ─────────────────────────

    async def search_stocks(self, keyword: str) -> list[dict]:
        """종목명 또는 코드로 검색 — 로컬 마스터 데이터 기반.

        KIS API에는 종목 검색 전용 엔드포인트가 없으므로,
        주요 국내 종목 마스터 데이터를 활용합니다.
        """
        keyword_upper = keyword.upper()
        results = []
        for code, name in MAJOR_STOCKS.items():
            if keyword_upper in code or keyword.lower() in name.lower() or keyword in name:
                results.append({"stock_code": code, "name": name})
        return results[:20]


# ── 주요 국내 종목 마스터 (확장 가능) ─────────────────
MAJOR_STOCKS: dict[str, str] = {
    "005930": "삼성전자",
    "000660": "SK하이닉스",
    "373220": "LG에너지솔루션",
    "207940": "삼성바이오로직스",
    "005380": "현대자동차",
    "006400": "삼성SDI",
    "051910": "LG화학",
    "035420": "NAVER",
    "000270": "기아",
    "035720": "카카오",
    "005490": "POSCO홀딩스",
    "068270": "셀트리온",
    "028260": "삼성물산",
    "105560": "KB금융",
    "055550": "신한지주",
    "003670": "포스코퓨처엠",
    "012330": "현대모비스",
    "066570": "LG전자",
    "096770": "SK이노베이션",
    "034730": "SK",
    "003550": "LG",
    "032830": "삼성생명",
    "030200": "KT",
    "017670": "SK텔레콤",
    "086790": "하나금융지주",
    "015760": "한국전력",
    "009150": "삼성전기",
    "033780": "KT&G",
    "018260": "삼성에스디에스",
    "316140": "우리금융지주",
    "036570": "엔씨소프트",
    "011200": "HMM",
    "259960": "크래프톤",
    "010130": "고려아연",
    "024110": "기업은행",
    "000810": "삼성화재",
    "329180": "현대중공업",
    "010950": "S-Oil",
    "003490": "대한항공",
    "034020": "두산에너빌리티",
    "352820": "하이브",
    "251270": "넷마블",
    "263750": "펄어비스",
    "112040": "위메이드",
    "293490": "카카오게임즈",
    "041510": "에스엠",
    "035900": "JYP Ent.",
    "122870": "와이지엔터테인먼트",
    "047810": "한국항공우주",
    "042700": "한미반도체",
}
