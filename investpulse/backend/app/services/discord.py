import httpx

from app.config import settings


class DiscordService:
    """Discord 웹훅을 통한 알림 전송."""

    @staticmethod
    async def send_alert(
        market: str,
        indicator: str,
        condition: str,
        current_value: float,
        threshold: float,
    ) -> None:
        if not settings.DISCORD_WEBHOOK_URL:
            return

        # 불리시: 녹색, 베어리시: 빨간색
        bullish_keywords = {"bullish", "oversold", "below_lower", "cross_up"}
        color = 0x26A69A if any(k in condition for k in bullish_keywords) else 0xEF5350

        embed = {
            "title": f"🔔 {market} {indicator} Alert",
            "description": f"**{indicator}** {condition} 신호 감지",
            "color": color,
            "fields": [
                {"name": "마켓", "value": market, "inline": True},
                {"name": "지표", "value": indicator, "inline": True},
                {"name": "현재값", "value": f"{current_value:.2f}", "inline": True},
                {"name": "기준값", "value": f"{threshold:.2f}", "inline": True},
                {"name": "조건", "value": condition, "inline": True},
            ],
            "footer": {"text": "InvestPulse Alert Engine"},
        }

        payload = {"username": "InvestPulse", "embeds": [embed]}

        async with httpx.AsyncClient() as client:
            await client.post(settings.DISCORD_WEBHOOK_URL, json=payload)
