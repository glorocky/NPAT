"""Deterministic AI trade-plan analytics for stocks and futures."""

from __future__ import annotations

from core.models import FuturesAnalysis, Quote


class TradeIdeaAnalytics:
    """Build explainable directional trade ideas without placing orders."""

    @staticmethod
    def _classify(score: float) -> str:
        if score >= 60:
            return "STRONG_BUY"
        if score >= 20:
            return "BUY"
        if score <= -60:
            return "STRONG_SELL"
        if score <= -20:
            return "SELL"
        return "WAIT"

    @staticmethod
    def _price_score(change_pct: float) -> float:
        return max(-100.0, min(100.0, change_pct / 2.0 * 100.0))

    @classmethod
    def stock_score(cls, quote: Quote, market_score: float) -> tuple[float, str, tuple[str, ...]]:
        price_score = cls._price_score((quote.last_price - quote.previous_close) / quote.previous_close * 100 if quote.previous_close else 0.0)
        score = price_score * 0.75 + max(-100.0, min(100.0, market_score)) * 0.25
        signal = cls._classify(score)
        reasons = (
            f"Stock price change is {((quote.last_price - quote.previous_close) / quote.previous_close * 100 if quote.previous_close else 0.0):+.2f}%.",
            f"Selected-index market regime contributes {market_score:+.1f} points of context.",
        )
        return round(score, 2), signal, reasons

    @classmethod
    def future_score(cls, future: FuturesAnalysis, market_score: float) -> tuple[float, str, tuple[str, ...]]:
        price_component = cls._price_score(future.price_change_pct)
        position_component = {
            "LONG_BUILDUP": 100.0,
            "SHORT_COVERING": 60.0,
            "SHORT_BUILDUP": -100.0,
            "LONG_UNWINDING": -60.0,
            "NEUTRAL": 0.0,
        }.get(future.positioning, 0.0)
        imbalance = max(-100.0, min(100.0, future.quantity_imbalance_pct * 2.0))
        score = price_component * 0.40 + position_component * 0.40 + imbalance * 0.10 + max(-100.0, min(100.0, market_score)) * 0.10
        signal = cls._classify(score)
        reasons = (
            f"Future price change is {future.price_change_pct:+.2f}%.",
            f"Futures positioning is {future.positioning} with OI change {future.oi_change_pct:+.2f}%.",
            f"Buy/sell quantity imbalance is {future.quantity_imbalance_pct:+.2f}%.",
            f"Selected-index market regime contributes {market_score:+.1f} points of context.",
        )
        return round(score, 2), signal, reasons
