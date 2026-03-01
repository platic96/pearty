import logging
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

from app.database import async_session_maker
from app.models.alert import Alert
from app.services.discord import DiscordService
from app.services.indicators import IndicatorService
from app.services.upbit import UpbitService

logger = logging.getLogger(__name__)


class AlertEngine:
    """주기적으로 활성 알림 조건을 체크하고 Discord로 알림을 발송하는 엔진."""

    def __init__(self, upbit_service: UpbitService) -> None:
        self.upbit = upbit_service
        self.scheduler = AsyncIOScheduler()

    def start(self) -> None:
        self.scheduler.add_job(
            self.check_alerts,
            "interval",
            minutes=5,
            id="alert_check",
            replace_existing=True,
        )
        self.scheduler.start()
        logger.info("AlertEngine started — checking alerts every 5 minutes")

    def shutdown(self) -> None:
        self.scheduler.shutdown(wait=False)
        logger.info("AlertEngine shut down")

    async def check_alerts(self) -> None:
        """활성 알림을 조회하여 조건 충족 시 Discord 알림 발송."""
        async with async_session_maker() as session:
            result = await session.execute(
                select(Alert).where(Alert.is_active == True)  # noqa: E712
            )
            alerts = result.scalars().all()

        if not alerts:
            return

        # 마켓별 그룹핑 — API 호출 최소화
        markets = set(alert.market for alert in alerts)

        for market in markets:
            try:
                raw_candles = await self.upbit.get_candles(market, "1d", 200)
                indicators = IndicatorService.calculate_all(raw_candles)
                market_alerts = [a for a in alerts if a.market == market]

                for alert in market_alerts:
                    triggered = self._evaluate(alert, indicators)
                    if triggered:
                        current_val = self._get_current_value(alert.indicator, indicators)
                        await DiscordService.send_alert(
                            market=alert.market,
                            indicator=alert.indicator,
                            condition=alert.condition,
                            current_value=current_val or 0,
                            threshold=alert.threshold,
                        )
                        await self._mark_triggered(alert.id)
                        logger.info(f"Alert triggered: {alert.market} {alert.indicator} {alert.condition}")
            except Exception:
                logger.exception(f"Error checking alerts for {market}")

    def _evaluate(self, alert: Alert, indicators: dict) -> bool:
        """알림 조건 평가."""
        current_val = self._get_current_value(alert.indicator, indicators)
        if current_val is None:
            return False

        if alert.condition == "above":
            return current_val > alert.threshold
        elif alert.condition == "below":
            return current_val < alert.threshold
        elif alert.condition == "cross_up":
            return indicators.get("macd", {}).get("signal") == "bullish_cross"
        elif alert.condition == "cross_down":
            return indicators.get("macd", {}).get("signal") == "bearish_cross"
        return False

    @staticmethod
    def _get_current_value(indicator: str, indicators: dict) -> float | None:
        if indicator == "RSI":
            return indicators.get("rsi", {}).get("current")
        elif indicator == "MACD":
            hist = indicators.get("macd", {}).get("histogram", [])
            return hist[-1] if hist else None
        elif indicator == "BB":
            return indicators.get("bollinger_bands", {}).get("bandwidth")
        return None

    @staticmethod
    async def _mark_triggered(alert_id: int) -> None:
        async with async_session_maker() as session:
            result = await session.execute(select(Alert).where(Alert.id == alert_id))
            alert = result.scalar_one_or_none()
            if alert:
                alert.last_triggered_at = datetime.utcnow()
                await session.commit()
