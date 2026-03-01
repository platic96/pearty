import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD
from ta.volatility import BollingerBands


class IndicatorService:
    """기술적 분석 지표 계산 — RSI, MACD, Bollinger Bands."""

    @staticmethod
    def calculate_all(candles: list[dict]) -> dict:
        """캔들 데이터로부터 모든 기술지표를 계산.

        Args:
            candles: [{timestamp, open, high, low, close, volume}, ...]

        Returns:
            {rsi: {...}, macd: {...}, bollinger_bands: {...}, timestamps: [...]}
        """
        df = pd.DataFrame(candles)
        close = df["close"].astype(float)

        return {
            "rsi": IndicatorService._calculate_rsi(close),
            "macd": IndicatorService._calculate_macd(close),
            "bollinger_bands": IndicatorService._calculate_bb(close),
            "timestamps": df["timestamp"].tolist(),
        }

    @staticmethod
    def _calculate_rsi(close: pd.Series, window: int = 14) -> dict:
        indicator = RSIIndicator(close=close, window=window)
        rsi_values = indicator.rsi()
        current = rsi_values.iloc[-1] if len(rsi_values) > 0 else None

        signal = "neutral"
        if current is not None and not pd.isna(current):
            if current > 70:
                signal = "overbought"
            elif current < 30:
                signal = "oversold"

        return {
            "values": rsi_values.fillna(0).tolist(),
            "current": round(float(current), 2) if current is not None and not pd.isna(current) else None,
            "signal": signal,
            "window": window,
        }

    @staticmethod
    def _calculate_macd(
        close: pd.Series,
        window_slow: int = 26,
        window_fast: int = 12,
        window_sign: int = 9,
    ) -> dict:
        indicator = MACD(
            close=close,
            window_slow=window_slow,
            window_fast=window_fast,
            window_sign=window_sign,
        )
        macd_line = indicator.macd()
        signal_line = indicator.macd_signal()
        histogram = indicator.macd_diff()

        signal = "neutral"
        if len(histogram) >= 2:
            prev, curr = histogram.iloc[-2], histogram.iloc[-1]
            if not pd.isna(prev) and not pd.isna(curr):
                if prev < 0 and curr > 0:
                    signal = "bullish_cross"
                elif prev > 0 and curr < 0:
                    signal = "bearish_cross"

        return {
            "macd_line": macd_line.fillna(0).tolist(),
            "signal_line": signal_line.fillna(0).tolist(),
            "histogram": histogram.fillna(0).tolist(),
            "signal": signal,
        }

    @staticmethod
    def _calculate_bb(close: pd.Series, window: int = 20, window_dev: int = 2) -> dict:
        indicator = BollingerBands(close=close, window=window, window_dev=window_dev)
        upper = indicator.bollinger_hband()
        middle = indicator.bollinger_mavg()
        lower = indicator.bollinger_lband()

        current_close = close.iloc[-1]
        signal = "neutral"
        if not pd.isna(upper.iloc[-1]) and not pd.isna(lower.iloc[-1]):
            if current_close > upper.iloc[-1]:
                signal = "above_upper"
            elif current_close < lower.iloc[-1]:
                signal = "below_lower"

        bandwidth = 0.0
        if not pd.isna(middle.iloc[-1]) and middle.iloc[-1] != 0:
            bandwidth = round(
                float((upper.iloc[-1] - lower.iloc[-1]) / middle.iloc[-1] * 100), 2
            )

        return {
            "upper": upper.fillna(0).tolist(),
            "middle": middle.fillna(0).tolist(),
            "lower": lower.fillna(0).tolist(),
            "signal": signal,
            "bandwidth": bandwidth,
        }
