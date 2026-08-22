from __future__ import annotations

import math
from dataclasses import dataclass

from risk.risk_models import PositionSizing, RiskDecision, RiskLimits


class RiskEngine:
    """Pure, paper-only risk gate. It never places broker orders."""

    def __init__(self, limits: RiskLimits | None = None):
        self.limits = limits or RiskLimits()

    def size_position(
        self,
        *,
        capital: float,
        entry: float,
        stop: float,
        lot_size: int = 1,
        max_quantity: int | None = None,
    ) -> PositionSizing:
        if capital <= 0 or entry <= 0 or stop <= 0:
            raise ValueError("capital, entry and stop must be positive")
        if lot_size <= 0:
            raise ValueError("lot_size must be positive")
        stop_distance = abs(entry - stop)
        if stop_distance <= 0:
            raise ValueError("entry and stop must be different")
        risk_amount = capital * self.limits.max_risk_per_trade_pct / 100.0
        units = math.floor(risk_amount / stop_distance)
        quantity = (units // lot_size) * lot_size
        if max_quantity is not None:
            quantity = min(quantity, (max_quantity // lot_size) * lot_size)
        return PositionSizing(
            quantity=max(0, quantity),
            risk_amount=round(max(0, quantity) * stop_distance, 2),
            capital_required=round(max(0, quantity) * entry, 2),
            stop_distance=round(stop_distance, 4),
            reason=("Position sized from stop distance and configured "
                    "maximum risk per trade."),
        )

    def validate_trade(
        self,
        *,
        entry: float,
        stop: float,
        target: float,
        capital: float,
        open_trades: int = 0,
        existing_exposure: float = 0.0,
    ) -> RiskDecision:
        reasons: list[str] = []
        warnings: list[str] = []
        if min(entry, stop, target, capital) <= 0:
            return RiskDecision(False, "BLOCK", ("Entry, stop, target and capital must be positive.",))
        if open_trades >= self.limits.max_open_trades:
            return RiskDecision(False, "BLOCK", ("Maximum open-trade limit reached.",))
        if stop == entry:
            return RiskDecision(False, "BLOCK", ("Stop cannot equal entry.",))
        reward = abs(target - entry)
        risk = abs(entry - stop)
        rr = reward / risk if risk else 0.0
        if rr < self.limits.min_risk_reward:
            return RiskDecision(False, "BLOCK", (f"Risk/reward {rr:.2f} is below minimum {self.limits.min_risk_reward:.2f}.",))
        exposure_pct = ((existing_exposure + entry) / capital) * 100.0
        if exposure_pct > self.limits.max_portfolio_exposure_pct:
            return RiskDecision(False, "BLOCK", (f"Projected exposure {exposure_pct:.1f}% exceeds {self.limits.max_portfolio_exposure_pct:.1f}%.",))
        reasons.append(f"Risk/reward {rr:.2f} passes the minimum gate.")
        if rr < 2.0:
            warnings.append("Moderate reward-to-risk; prefer the hedged structure.")
        return RiskDecision(True, "LOW" if rr >= 2 else "MEDIUM", tuple(reasons), tuple(warnings))

    def validate_hedge(self, *, primary_price: float, hedge_price: float, hedge_ratio_pct: float = 25.0) -> RiskDecision:
        if primary_price <= 0 or hedge_price <= 0:
            return RiskDecision(False, "BLOCK", ("Primary and hedge prices must be positive.",))
        if hedge_ratio_pct <= 0 or hedge_ratio_pct > 100:
            return RiskDecision(False, "BLOCK", ("Invalid hedge ratio.",))
        warnings = () if hedge_ratio_pct <= 35 else ("Hedge premium is relatively high; verify payoff before entry.",)
        return RiskDecision(True, "LOW" if hedge_ratio_pct <= 25 else "MEDIUM", ("Protective hedge is structurally valid.",), warnings)
