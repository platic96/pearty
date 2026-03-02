import logging
from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import func, select

from app.database import async_session_maker
from app.models.alert import Alert
from app.models.alert_history import AlertHistory
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

                # PRICE/CHANGE_RATE용 현재가 정보
                current_close = raw_candles[-1]["close"] if raw_candles else None

                market_alerts = [a for a in alerts if a.market == market]

                for alert in market_alerts:
                    # 쿨다운 체크
                    if not self._cooldown_passed(alert):
                        continue

                    triggered = self._evaluate(alert, indicators, raw_candles, current_close)
                    if triggered:
                        current_val = self._get_current_value(
                            alert.indicator, indicators, raw_candles, current_close
                        )
                        # 히스토리 기록 + Discord 알림
                        await self._handle_trigger(
                            alert, current_val, indicators
                        )
            except Exception:
                logger.exception(f"Error checking alerts for {market}")

    @staticmethod
    def _cooldown_passed(alert: Alert) -> bool:
        """쿨다운 시간이 지났는지 확인."""
        if alert.last_triggered_at is None:
            return True
        if alert.cooldown_minutes <= 0:
            return True
        cooldown_end = alert.last_triggered_at + timedelta(minutes=alert.cooldown_minutes)
        return datetime.utcnow() >= cooldown_end

    def _evaluate(
        self,
        alert: Alert,
        indicators: dict,
        candles: list[dict],
        current_close: float | None,
    ) -> bool:
        """알림 조건 평가."""
        if alert.indicator == "CHANGE_RATE":
            return self._evaluate_change_rate(alert, candles)

        current_val = self._get_current_value(
            alert.indicator, indicators, candles, current_close
        )
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
    def _evaluate_change_rate(alert: Alert, candles: list[dict]) -> bool:
        """변동률 조건 평가. threshold는 변동률(%), condition은 above/below."""
        if len(candles) < 2:
            return False
        current = candles[-1]["close"]
        previous = candles[-2]["close"]
        if previous == 0:
            return False
        change_pct = abs((current - previous) / previous * 100)
        return change_pct > alert.threshold

    @staticmethod
    def _get_current_value(
        indicator: str,
        indicators: dict,
        candles: list[dict],
        current_close: float | None,
    ) -> float | None:
        if indicator == "RSI":
            return indicators.get("rsi", {}).get("current")
        elif indicator == "MACD":
            hist = indicators.get("macd", {}).get("histogram", [])
            return hist[-1] if hist else None
        elif indicator == "BB":
            return indicators.get("bollinger_bands", {}).get("bandwidth")
        elif indicator == "PRICE":
            return current_close
        elif indicator == "CHANGE_RATE":
            if len(candles) < 2:
                return None
            current = candles[-1]["close"]
            previous = candles[-2]["close"]
            if previous == 0:
                return None
            return abs((current - previous) / previous * 100)
        return None

    async def _handle_trigger(
        self, alert: Alert, current_val: float | None, indicators: dict
    ) -> None:
        """알림 발동 처리: 히스토리 기록 → Discord 전송 → 상태 업데이트."""
        # 히스토리 레코드 생성
        history = AlertHistory(
            alert_id=alert.id,
            triggered_at=datetime.utcnow(),
            indicator_value=current_val,
            threshold=alert.threshold,
            status="triggered",
        )

        # Discord 전송 시도
        try:
            success = await DiscordService.send_alert(
                market=alert.market,
                indicator=alert.indicator,
                condition=alert.condition,
                current_value=current_val or 0,
                threshold=alert.threshold,
                indicators=indicators,
            )
            history.status = "sent" if success else "failed"
            if not success:
                history.message = "Discord webhook delivery failed"
        except Exception as e:
            history.status = "failed"
            history.message = str(e)[:500]
            logger.exception(f"Discord send failed for alert {alert.id}")

        # DB에 기록
        async with async_session_maker() as session:
            session.add(history)

            result = await session.execute(select(Alert).where(Alert.id == alert.id))
            db_alert = result.scalar_one_or_none()
            if db_alert:
                db_alert.last_triggered_at = datetime.utcnow()

            await session.commit()

        logger.info(
            f"Alert triggered: {alert.market} {alert.indicator} "
            f"{alert.condition} (status={history.status})"
        )

    @staticmethod
    async def get_trigger_count(alert_id: int) -> int:
        """특정 알림의 발동 횟수 조회."""
        async with async_session_maker() as session:
            result = await session.execute(
                select(func.count(AlertHistory.id)).where(
                    AlertHistory.alert_id == alert_id
                )
            )
            return result.scalar() or 0
