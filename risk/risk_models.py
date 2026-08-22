from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class RiskLimits:
    max_risk_per_trade_pct: float = 1.0
    max_daily_loss_pct: float = 2.0
    max_portfolio_exposure_pct: float = 30.0
    max_open_trades: int = 5
    min_risk_reward: float = 1.5
    max_hedge_premium_pct_of_primary: float = 35.0


@dataclass(frozen=True, slots=True)
class PositionSizing:
    quantity: int
    risk_amount: float
    capital_required: float
    stop_distance: float
    reason: str


@dataclass(frozen=True, slots=True)
class RiskDecision:
    approved: bool
    risk_level: str
    reasons: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)
