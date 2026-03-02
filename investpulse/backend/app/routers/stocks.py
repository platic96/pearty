"""주식 시세 / 차트 / 검색 / 기술지표 라우터."""

from fastapi import APIRouter, Depends, HTTPException, Query

from app.services.indicators import IndicatorService
from app.services.kis import KISService

router = APIRouter(prefix="/api/stocks", tags=["stocks"])

_kis_service = KISService()


def get_kis_service() -> KISService:
    return _kis_service


@router.get("/status")
async def kis_status(kis: KISService = Depends(get_kis_service)):
    """한국투자증권 API 연결 상태 확인."""
    return {
        "configured": kis.is_configured(),
        "message": "API 키가 설정되어 있습니다." if kis.is_configured() else "KIS_APP_KEY / KIS_APP_SECRET을 .env에 설정해주세요.",
    }


@router.get("/search")
async def search_stocks(
    q: str = Query(..., min_length=1, description="종목명 또는 코드"),
    kis: KISService = Depends(get_kis_service),
):
    """종목 검색."""
    return await kis.search_stocks(q)


@router.get("/price/{stock_code}")
async def get_stock_price(
    stock_code: str,
    kis: KISService = Depends(get_kis_service),
):
    """주식 현재가 조회."""
    if not kis.is_configured():
        raise HTTPException(status_code=503, detail="한국투자증권 API 키가 설정되지 않았습니다")
    try:
        return await kis.get_stock_price(stock_code)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"주식 시세 조회 실패: {e}")


@router.get("/candles/{stock_code}")
async def get_stock_candles(
    stock_code: str,
    period: str = Query("D", description="D=일봉, W=주봉, M=월봉"),
    count: int = Query(100, ge=1, le=300),
    kis: KISService = Depends(get_kis_service),
):
    """주식 캔들 데이터 조회."""
    if not kis.is_configured():
        raise HTTPException(status_code=503, detail="한국투자증권 API 키가 설정되지 않았습니다")
    try:
        return await kis.get_stock_candles(stock_code, period=period, count=count)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"주식 캔들 조회 실패: {e}")


@router.get("/indicators/{stock_code}")
async def get_stock_indicators(
    stock_code: str,
    period: str = Query("D", description="D=일봉, W=주봉, M=월봉"),
    count: int = Query(200, ge=50, le=300),
    kis: KISService = Depends(get_kis_service),
):
    """주식 기술지표 계산 (RSI, MACD, BB)."""
    if not kis.is_configured():
        raise HTTPException(status_code=503, detail="한국투자증권 API 키가 설정되지 않았습니다")
    try:
        candles = await kis.get_stock_candles(stock_code, period=period, count=count)
        if len(candles) < 30:
            raise HTTPException(status_code=400, detail="기술지표 계산에 충분한 데이터가 없습니다 (최소 30개)")
        return IndicatorService.calculate_all(candles)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"주식 지표 계산 실패: {e}")
