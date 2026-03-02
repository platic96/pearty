import logging
from datetime import datetime

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class DiscordService:
    """Discord 웹훅을 통한 알림 전송."""

    @staticmethod
    async def send_alert(
        market: str,
        indicator: str,
        condition: str,
        current_value: float,
        threshold: float,
        indicators: dict | None = None,
    ) -> bool:
        """알림을 Discord 웹훅으로 전송. 성공 시 True 반환."""
        if not settings.DISCORD_WEBHOOK_URL:
            return False

        # 불리시: 녹색, 베어리시: 빨간색
        bullish_keywords = {"above", "cross_up"}
        bearish_keywords = {"below", "cross_down"}
        if condition in bullish_keywords:
            color = 0x26A69A
        elif condition in bearish_keywords:
            color = 0xEF5350
        else:
            color = 0x6366F1

        condition_labels = {
            "above": "이상 (Above)",
            "below": "이하 (Below)",
            "cross_up": "골든크로스 (Golden Cross)",
            "cross_down": "데드크로스 (Dead Cross)",
        }

        fields = [
            {"name": "마켓 (Market)", "value": market, "inline": True},
            {"name": "지표 (Indicator)", "value": indicator, "inline": True},
            {"name": "조건 (Condition)", "value": condition_labels.get(condition, condition), "inline": True},
            {"name": "현재값 (Current)", "value": f"`{current_value:,.2f}`", "inline": True},
            {"name": "기준값 (Threshold)", "value": f"`{threshold:,.2f}`", "inline": True},
        ]

        # 추가 지표 정보 포함
        if indicators:
            rsi = indicators.get("rsi", {}).get("current")
            macd_signal = indicators.get("macd", {}).get("signal")
            bb_signal = indicators.get("bollinger_bands", {}).get("signal")
            extra_parts = []
            if rsi is not None:
                rsi_emoji = "🔴" if rsi > 70 else "🟢" if rsi < 30 else "⚪"
                extra_parts.append(f"RSI: {rsi_emoji} {rsi:.1f}")
            if macd_signal:
                extra_parts.append(f"MACD: {macd_signal}")
            if bb_signal:
                extra_parts.append(f"BB: {bb_signal}")
            if extra_parts:
                fields.append({
                    "name": "지표 요약 (Indicator Summary)",
                    "value": " | ".join(extra_parts),
                    "inline": False,
                })

        embed = {
            "title": f"🔔 {market} {indicator} Alert",
            "description": f"**{indicator}** {condition_labels.get(condition, condition)} 조건이 발동되었습니다.",
            "color": color,
            "fields": fields,
            "footer": {"text": "InvestPulse Alert Engine"},
            "timestamp": datetime.utcnow().isoformat(),
        }

        payload = {"username": "InvestPulse", "embeds": [embed]}

        # 1회 재시도 로직
        for attempt in range(2):
            try:
                async with httpx.AsyncClient(timeout=10) as client:
                    resp = await client.post(settings.DISCORD_WEBHOOK_URL, json=payload)
                    if resp.status_code in (200, 204):
                        return True
                    logger.warning(
                        f"Discord webhook returned {resp.status_code} (attempt {attempt + 1})"
                    )
            except Exception:
                logger.warning(f"Discord webhook request failed (attempt {attempt + 1})")

        return False
