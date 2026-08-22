from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable


@dataclass(frozen=True, slots=True)
class BacktestTrade:
    entry: float
    exit: float
    side: str
    quantity: int
    pnl: float


@dataclass(frozen=True, slots=True)
class BacktestResult:
    trades: tuple[BacktestTrade, ...]
    net_pnl: float
    win_rate: float
    max_drawdown: float


class BacktestEngine:
    """Simple deterministic candle-by-candle strategy harness."""

    @staticmethod
    def run(candles: Iterable, signal_fn: Callable[[object], str], quantity: int = 1) -> BacktestResult:
        open_trade = None
        closed: list[BacktestTrade] = []
        equity = 0.0
        peak = 0.0
        max_dd = 0.0
        for candle in candles:
            price = float(getattr(candle, "close", getattr(candle, "last_price", 0)))
            if price <= 0:
                continue
            signal = str(signal_fn(candle)).upper()
            if open_trade is None and signal in {"BUY", "SELL"}:
                open_trade = (signal, price)
            elif open_trade is not None and signal in {"BUY", "SELL", "EXIT"}:
                side, entry = open_trade
                pnl = (price - entry) * quantity if side == "BUY" else (entry - price) * quantity
                trade = BacktestTrade(entry, price, side, quantity, pnl)
                closed.append(trade)
                equity += pnl
                peak = max(peak, equity)
                max_dd = max(max_dd, peak - equity)
                open_trade = None
        wins = sum(t.pnl > 0 for t in closed)
        return BacktestResult(tuple(closed), round(equity, 2), (wins / len(closed) * 100) if closed else 0.0, round(max_dd, 2))
