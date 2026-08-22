from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True, slots=True)
class HedgeLeg:
    action: str
    instrument: str
    option_type: str
    strike: int | None
    entry_price: float
    trading_symbol: str = ""
    expiry: str = ""
    reason: str = ""


@dataclass(frozen=True, slots=True)
class TradePlan:
    asset_class: str
    action: str
    symbol: str
    entry_price: float
    stop_loss: float
    target: float
    confidence: float
    rationale: tuple[str, ...]
    hedge: HedgeLeg | None = None
    paper_only: bool = True
    status: str = "REVIEW"


class TradePlanner:
    """Builds explainable buy/sell plans. It never submits an order."""

    @staticmethod
    def _find_hedge(options: Iterable, direction: str, spot: float):
        rows = [o for o in options if getattr(o, "strike_price", 0) > 0]
        if not rows:
            return None
        strikes = sorted({int(o.strike_price) for o in rows})
        atm = min(strikes, key=lambda x: abs(x - spot))
        step = min((b - a for a, b in zip(strikes, strikes[1:]) if b > a), default=0)
        if direction == "BULLISH":
            wanted = atm - step if step else atm
            candidates = [o for o in rows if int(o.strike_price) == wanted and getattr(o, "put_ltp", 0) > 0]
            if not candidates:
                candidates = [o for o in rows if int(o.strike_price) == atm and getattr(o, "put_ltp", 0) > 0]
            if not candidates:
                return None
            o = candidates[0]
            return HedgeLeg("BUY", "PUT", "PE", int(o.strike_price), float(o.put_ltp), o.put_trading_symbol, o.expiry,
                            "Protective put against a bullish future/stock position.")
        wanted = atm + step if step else atm
        candidates = [o for o in rows if int(o.strike_price) == wanted and getattr(o, "call_ltp", 0) > 0]
        if not candidates:
            candidates = [o for o in rows if int(o.strike_price) == atm and getattr(o, "call_ltp", 0) > 0]
        if not candidates:
            return None
        o = candidates[0]
        return HedgeLeg("BUY", "CALL", "CE", int(o.strike_price), float(o.call_ltp), o.call_trading_symbol, o.expiry,
                        "Protective call against a bearish future/stock position.")

    @classmethod
    def build_future_plan(cls, futures, options) -> TradePlan:
        bullish = futures.price_change_pct >= 0 and futures.positioning in {"LONG_BUILDUP", "SHORT_COVERING"}
        bearish = futures.price_change_pct < 0 and futures.positioning in {"SHORT_BUILDUP", "LONG_UNWINDING"}
        if bullish:
            action = "BUY FUTURE"
            stop = futures.futures_price - max(abs(futures.futures_price * 0.004), 1.0)
            target = futures.futures_price + max(abs(futures.futures_price * 0.008), 2.0)
            direction = "BULLISH"
        elif bearish:
            action = "SELL FUTURE"
            stop = futures.futures_price + max(abs(futures.futures_price * 0.004), 1.0)
            target = futures.futures_price - max(abs(futures.futures_price * 0.008), 2.0)
            direction = "BEARISH"
        else:
            return TradePlan("FUTURE", "NO TRADE", futures.symbol, futures.futures_price, 0, 0, 0,
                             ("Futures evidence is mixed; no directional future trade is recommended.",), status="NO_TRADE")
        hedge = cls._find_hedge(options, direction, futures.spot_price)
        reasons = (
            f"Futures positioning: {futures.positioning}.",
            f"Futures change: {futures.price_change_pct:.2f}%.",
            "Use the protective option as a hedge, not as a second directional bet.",
        )
        return TradePlan("FUTURE", action, futures.trading_symbol, futures.futures_price, stop, target,
                         65.0 if hedge else 55.0, reasons, hedge, True, "REVIEW")

    @classmethod
    def build_stock_plan(cls, stock, direction: str, option_chain=None) -> TradePlan:
        if direction == "BULLISH":
            action = "BUY STOCK"
            stop = stock.last_price * 0.99
            target = stock.last_price * 1.02
        elif direction == "BEARISH":
            action = "SELL STOCK"
            stop = stock.last_price * 1.01
            target = stock.last_price * 0.98
        else:
            return TradePlan("STOCK", "NO TRADE", stock.symbol, stock.last_price, 0, 0, 0,
                             ("Stock direction is neutral.",), status="NO_TRADE")
        hedge = cls._find_hedge(option_chain or [], direction, stock.last_price)
        reasons = (
            f"Selected {stock.symbol} from the selected-index movers.",
            f"Current change is {stock.change_pct:.2f}%.",
            "Stock trade is only a candidate; confirm liquidity and the underlying setup before paper entry.",
        )
        return TradePlan("STOCK", action, stock.symbol, stock.last_price, stop, target,
                         60.0 if hedge else 50.0, reasons, hedge, True, "REVIEW")
