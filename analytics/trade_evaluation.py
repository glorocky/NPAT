from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TradeEvaluation:
    total: int
    wins: int
    losses: int
    win_rate: float
    net_pnl: float
    expectancy: float


def evaluate(pnls: list[float]) -> TradeEvaluation:
    wins = sum(p > 0 for p in pnls)
    losses = sum(p < 0 for p in pnls)
    total = len(pnls)
    net = sum(pnls)
    return TradeEvaluation(total, wins, losses, (wins / total * 100) if total else 0.0,
                           net, (net / total) if total else 0.0)
