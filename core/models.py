"""
=========================================================
NPAT - Core Data Models
=========================================================

Purpose
-------
Central strongly-typed data models used throughout NPAT.

These dataclasses replace dictionaries across the application,
providing type safety, IDE auto-completion, easier debugging,
and cleaner architecture.

Author  : Rocky Chopra
Version : 3.0.0
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


# =========================================================
# Quote
# =========================================================

@dataclass(frozen=True, slots=True)
class Quote:
    """
    Represents a live market quote.
    """

    symbol: str
    exchange: str

    last_price: float

    open: float
    high: float
    low: float
    previous_close: float

    volume: int = 0

    timestamp: Optional[datetime] = None


# =========================================================
# Historical Candle
# =========================================================

@dataclass(frozen=True, slots=True)
class HistoricalCandle:
    """
    Represents one historical OHLCV candle.
    """

    timestamp: datetime

    open: float
    high: float
    low: float
    close: float

    volume: int
    
# =========================================================
# Futures Contract Data
# =========================================================

@dataclass(frozen=True, slots=True)
class FutureData:
    """
    Normalized futures contract market data.

    Represents one futures contract and contains both
    contract metadata and live market information.

    Provider-specific responses must be normalized into
    this model before reaching analytics or service layers.
    """

    symbol: str
    exchange: str

    trading_symbol: str
    expiry: str

    # -----------------------------
    # Contract Metadata
    # -----------------------------

    lot_size: int = 0
    exchange_token: str = ""

    # -----------------------------
    # Price
    # -----------------------------

    last_price: float = 0.0

    open: float = 0.0
    high: float = 0.0
    low: float = 0.0
    previous_close: float = 0.0

    # -----------------------------
    # Open Interest
    # -----------------------------

    open_interest: int = 0
    previous_open_interest: int = 0

    oi_change: int = 0
    oi_change_pct: float = 0.0

    # -----------------------------
    # Activity
    # -----------------------------

    volume: int = 0
    last_trade_quantity: int = 0

    total_buy_quantity: int = 0
    total_sell_quantity: int = 0

    # -----------------------------
    # Time
    # -----------------------------

    timestamp: Optional[datetime] = None
    

# =========================================================
# Futures Analysis
# =========================================================

@dataclass(frozen=True, slots=True)
class FuturesAnalysis:
    """
    Derived analytics for one futures contract.

    Built from normalized FutureData plus the underlying
    spot price. Contains futures-specific analytical values
    without provider-specific fields.
    """

    symbol: str
    exchange: str

    trading_symbol: str
    expiry: str

    # -----------------------------
    # Price Context
    # -----------------------------

    spot_price: float
    futures_price: float

    basis: float
    basis_pct: float

    previous_price: float
    price_change: float
    price_change_pct: float

    # -----------------------------
    # Open Interest
    # -----------------------------

    previous_oi: int
    current_oi: int

    oi_change: int
    oi_change_pct: float

    # -----------------------------
    # Positioning
    # -----------------------------

    positioning: str

    # -----------------------------
    # Market Activity
    # -----------------------------

    volume: int

    total_buy_quantity: int
    total_sell_quantity: int

    quantity_imbalance: int
    quantity_imbalance_pct: float

    # -----------------------------
    # Contract
    # -----------------------------

    lot_size: int = 0


# =========================================================
# Option Chain Strike
# =========================================================

@dataclass(frozen=True, slots=True)
class OptionData:
    """
    Represents one option strike.

    Contains both Call and Put information
    for a single strike.
    """

    strike_price: int

    expiry: str

    underlying_price: float

    # -----------------------------
    # Call Side
    # -----------------------------

    call_oi: int = 0

    call_change_oi: int = 0

    call_volume: int = 0

    call_iv: float = 0.0

    call_ltp: float = 0.0

    # -----------------------------
    # Put Side
    # -----------------------------

    put_oi: int = 0

    put_change_oi: int = 0

    put_volume: int = 0

    put_iv: float = 0.0

    put_ltp: float = 0.0


# =========================================================
# Market Level
# =========================================================

@dataclass(frozen=True, slots=True)
class MarketLevel:
    """
    Represents an important option-chain level.

    Used for:

    • Support
    • Resistance
    • Future Call Writing
    • Future Put Writing
    """

    strike: int

    open_interest: int

    change_in_oi: int = 0
    
# =========================================================
# Option Greeks
# =========================================================
@dataclass(frozen=True,slots=True)
class OptionGreeks:
    """
    Standardized option Greeks returned by all providers.
    """
    symbol: str
    expiry: str
    strike_price: int
    option_type: str
    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float
    iv: float

# =========================================================
# Option Premium Analysis
# =========================================================

@dataclass(frozen=True, slots=True)
class PremiumAnalysis:
    """
    Represents theoretical vs market premium analysis
    for one option contract.

    Used by:
    - Black-Scholes analytics
    - ATM strike analysis
    - Dashboard
    - Prediction Engine
    - Decision Engine
    """

    symbol: str

    expiry: str

    strike_price: int

    option_type: str

    underlying_price: float

    # -----------------------------
    # Premium
    # -----------------------------

    market_premium: float

    theoretical_premium: float

    premium_difference: float

    premium_difference_pct: float

    # -----------------------------
    # Volatility
    # -----------------------------

    iv: float

    # -----------------------------
    # Greeks
    # -----------------------------

    delta: float = 0.0

    gamma: float = 0.0

    theta: float = 0.0

    vega: float = 0.0

    rho: float = 0.0

    # -----------------------------
    # Contract Context
    # -----------------------------

    moneyness: str = ""

    time_to_expiry: float = 0.0

# =========================================================
# Put-Call Parity Analysis
# =========================================================

@dataclass(frozen=True, slots=True)
class ParityAnalysis:
    """
    Represents put-call parity and implied-forward analysis
    for one option strike.

    Used to validate option pricing relationships before
    premium deviations are consumed by downstream engines.
    """

    symbol: str

    expiry: str

    strike_price: int

    spot_price: float

    # -----------------------------
    # Market Premiums
    # -----------------------------

    call_premium: float

    put_premium: float

    # -----------------------------
    # Forward Analysis
    # -----------------------------

    implied_forward: float

    forward_premium: float

    forward_premium_pct: float

    # -----------------------------
    # Put-Call Parity
    # -----------------------------

    market_parity: float

    theoretical_parity: float

    parity_deviation: float

    parity_deviation_pct: float

    # -----------------------------
    # Time
    # -----------------------------

    time_to_expiry: float
    
# =========================================================
# Forward-Aware Premium Analysis
# =========================================================

@dataclass(frozen=True, slots=True)
class ForwardPremiumAnalysis:
    """
    Forward-aware option premium analysis.

    Compares:
    - Market premium
    - Spot-based Black-Scholes premium
    - Forward-aware theoretical premium

    Used to determine whether apparent premium deviation
    is explained by forward/carry effects.
    """

    symbol: str
    expiry: str

    strike_price: int
    option_type: str

    spot_price: float
    implied_forward: float

    # -----------------------------
    # Market
    # -----------------------------

    market_premium: float

    # -----------------------------
    # Theoretical Premiums
    # -----------------------------

    spot_bs_premium: float
    forward_bs_premium: float

    # -----------------------------
    # Spot-BS Deviation
    # -----------------------------

    spot_difference: float
    spot_difference_pct: float

    # -----------------------------
    # Forward-BS Deviation
    # -----------------------------

    forward_difference: float
    forward_difference_pct: float

    # -----------------------------
    # Inputs
    # -----------------------------

    iv: float
    time_to_expiry: float

    # -----------------------------
    # Context
    # -----------------------------

    moneyness: str = ""

# =========================================================
# Market Snapshot
# =========================================================

@dataclass(frozen=True, slots=True)
class MarketSnapshot:
    """
    Complete analytical market snapshot.

    Generated by the analytics engine and
    consumed by:

    • Dashboard
    • AI Engine
    • Telegram Alerts
    • Trading Strategies
    """

    symbol: str

    exchange: str = "NSE"

    spot_price: float = 0.0

    expiry: str = ""

    atm_strike: int = 0

    pcr: float = 0.0

    max_pain: Optional[int] = None

    support: list[MarketLevel] = field(default_factory=list)

    resistance: list[MarketLevel] = field(default_factory=list)

    total_call_oi: int = 0

    total_put_oi: int = 0

    option_chain: list[OptionData] = field(default_factory=list)
    
    # -----------------------------------------------------
    # Positioning Analytics
    # -----------------------------------------------------

    positioning_summary: Optional[PositioningSummary] = None

    atm_positioning_summary: Optional[PositioningSummary] = None

    positioning: list[PositioningAnalysis] = field(
        default_factory=list
    )

    atm_positioning: list[PositioningAnalysis] = field(
        default_factory=list
    )

    top_oi_additions: list[PositioningAnalysis] = field(
        default_factory=list
    )

    top_oi_reductions: list[PositioningAnalysis] = field(
        default_factory=list
    )


    timestamp: datetime = field(default_factory=datetime.now)
    
# =========================================================
# Greeks Analysis
# =========================================================

@dataclass(frozen=True, slots=True)
class GreeksAnalysis:
    """
    Analytics model for one option contract.

    Represents normalized Greeks for a CE or PE contract
    within the selected ATM strike window.
    """

    symbol: str
    expiry: str

    strike_price: int
    option_type: str

    spot_price: float
    option_ltp: float

    # -----------------------------
    # Greeks
    # -----------------------------

    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float

    # -----------------------------
    # Volatility
    # -----------------------------

    iv: float

    # -----------------------------
    # Context
    # -----------------------------

    moneyness: str = ""
    
# =========================================================
# Greeks Summary
# =========================================================

@dataclass(frozen=True, slots=True)
class GreeksSummary:
    """
    Aggregated interpretation of ATM-window option Greeks.

    Built from normalized GreeksAnalysis contracts and
    consumed by dashboard, AI and decision-engine layers.
    """

    symbol: str
    expiry: str

    spot_price: float
    atm_strike: int

    # -----------------------------
    # ATM Delta
    # -----------------------------

    atm_call_delta: float
    atm_put_delta: float
    delta_balance: float

    # -----------------------------
    # IV / Skew
    # -----------------------------

    atm_call_iv: float
    atm_put_iv: float
    iv_skew: float

    # -----------------------------
    # Gamma
    # -----------------------------

    highest_gamma_strike: int
    highest_gamma: float

    # -----------------------------
    # Theta
    # -----------------------------

    total_call_theta: float
    total_put_theta: float
    total_theta: float

    # -----------------------------
    # Vega
    # -----------------------------

    total_call_vega: float
    total_put_vega: float
    total_vega: float
    
# =========================================================
# VIX Range Analysis
# =========================================================

@dataclass(frozen=True, slots=True)
class VixRangeAnalysis:
    """
    Expected NIFTY daily range derived from India VIX.

    Contains both the VIX-implied range and the actual
    intraday range achieved so far.
    """

    symbol: str

    # -----------------------------
    # Market Inputs
    # -----------------------------

    reference_price: float
    india_vix: float

    day_open: float
    day_high: float
    day_low: float
    current_price: float

    # -----------------------------
    # Expected Move
    # -----------------------------

    expected_move_pct: float
    expected_move_points: float

    expected_lower: float
    expected_upper: float

    expected_total_range: float

    # -----------------------------
    # Actual Intraday Range
    # -----------------------------

    actual_range: float
    actual_range_pct: float

    range_achieved_pct: float
    
    # -----------------------------
    # Directional Range Usage
    # -----------------------------

    upside_achieved_points: float
    downside_achieved_points: float

    upside_achieved_pct: float
    downside_achieved_pct: float

    # -----------------------------
    # Remaining Range
    # -----------------------------

    upside_remaining: float
    downside_remaining: float
    
    # -----------------------------
    # Unused Expected Allowance
    # -----------------------------

    unused_upside_points: float
    unused_downside_points: float

    upside_breach_points: float
    downside_breach_points: float

    # -----------------------------
    # Range State
    # -----------------------------

    upper_range_exceeded: bool
    lower_range_exceeded: bool

    expected_range_exceeded: bool

# =========================================================
# OI Analysis
# =========================================================

@dataclass(frozen=True, slots=True)
class OIAnalysis:
    """
    Open Interest change analysis for one option contract.

    Tracks both session-level and interval-level OI change.
    """

    symbol: str
    expiry: str
    strike_price: int
    option_type: str

    current_oi: int

    # Session baseline
    session_baseline_oi: int
    session_change_oi: int
    session_change_oi_pct: float

    # Previous polling snapshot
    previous_oi: int
    interval_change_oi: int
    interval_change_oi_pct: float
    
# =========================================================
# OI Snapshot
# =========================================================

@dataclass(frozen=True, slots=True)
class OISnapshot:
    """
    One observed OI state for an option contract.
    """

    symbol: str
    expiry: str
    strike_price: int
    option_type: str

    open_interest: int
    price: float
    timestamp: datetime

# =========================================================
# Positioning Analysis
# =========================================================

@dataclass(frozen=True, slots=True)
class PositioningAnalysis:
    """
    Price and Open Interest positioning analysis
    for one market contract.
    """

    symbol: str
    expiry: str
    strike_price: int
    option_type: str

    previous_price: float
    current_price: float
    price_change: float
    price_change_pct: float

    previous_oi: int
    current_oi: int
    oi_change: int
    oi_change_pct: float

    classification: str
    
# =========================================================
# Positioning Summary
# =========================================================

@dataclass(frozen=True, slots=True)
class PositioningSummary:
    """
    Aggregated positioning counts for an option chain.

    Contains combined totals plus separate CE and PE counts.
    """

    # -----------------------------------------------------
    # Total Contracts
    # -----------------------------------------------------

    total_contracts: int

    # -----------------------------------------------------
    # Combined Classification Counts
    # -----------------------------------------------------

    long_buildup: int
    short_buildup: int
    long_unwinding: int
    short_covering: int
    neutral: int

    # -----------------------------------------------------
    # CE Classification Counts
    # -----------------------------------------------------

    ce_total: int

    ce_long_buildup: int
    ce_short_buildup: int
    ce_long_unwinding: int
    ce_short_covering: int
    ce_neutral: int

    # -----------------------------------------------------
    # PE Classification Counts
    # -----------------------------------------------------

    pe_total: int

    pe_long_buildup: int
    pe_short_buildup: int
    pe_long_unwinding: int
    pe_short_covering: int
    pe_neutral: int
    
# =========================================================
# Heatmap Stock
# =========================================================

@dataclass(frozen=True, slots=True)
class HeatmapStock:
    """
    Heatmap analytics for one index constituent.
    """

    symbol: str
    company_name: str
    sector: str
    exchange: str

    last_price: float
    previous_close: float

    change: float
    change_pct: float

    open: float
    high: float
    low: float

    direction: str
    
# =========================================================
# Heatmap Summary
# =========================================================

@dataclass(frozen=True, slots=True)
class HeatmapSummary:
    """
    Aggregate market breadth summary for an index heatmap.
    """

    total_stocks: int

    gainers: int
    losers: int
    flat: int

    advance_decline_ratio: float

    average_change_pct: float

    strongest_symbol: str
    strongest_change_pct: float

    weakest_symbol: str
    weakest_change_pct: float
    
# =========================================================
# Sector Breadth
# =========================================================

@dataclass(frozen=True, slots=True)
class SectorBreadth:
    """
    Aggregate market breadth for one index sector.
    """

    sector: str

    total_stocks: int

    gainers: int
    losers: int
    flat: int

    advance_decline_ratio: float
    breadth_pct: float

    average_change_pct: float

    strongest_symbol: str
    strongest_change_pct: float

    weakest_symbol: str
    weakest_change_pct: float
    
# =========================================================
# Sector Strength
# =========================================================

@dataclass(frozen=True, slots=True)
class SectorStrength:
    """
    Interpreted strength of one market sector.

    Combines sector breadth and average constituent
    performance into a normalized directional assessment.
    """

    sector: str

    total_stocks: int

    breadth_pct: float
    average_change_pct: float

    strength_score: float

    classification: str

    strongest_symbol: str
    weakest_symbol: str
    
# =========================================================
# Market Regime Analysis
# =========================================================

@dataclass(frozen=True, slots=True)
class MarketRegimeAnalysis:
    """
    Aggregate directional market regime derived from
    futures, breadth, sector participation and volatility.
    """

    regime: str
    regime_score: float

    futures_score: float
    breadth_score: float
    sector_score: float
    volatility_score: float

    bullish_sectors: int
    bearish_sectors: int
    neutral_sectors: int

    strongest_sector: str
    weakest_sector: str

    confidence: float

    reasons: tuple[str, ...]
# =========================================================
# Decision Analysis
# =========================================================
      
@dataclass
class DecisionAnalysis:
    """
    Deterministic NPAT trading decision produced from
    analyzed market evidence.
    """

    signal: str
    confidence: float
    score: float

    market_regime: str
    market_regime_score: float

    bullish_evidence: int
    bearish_evidence: int
    neutral_evidence: int

    reasons: tuple[str, ...]
    
# =========================================================
# AIService
# =========================================================
    
@dataclass
class AIAnalysis:
    """
    Final AI-layer analysis exposed to MarketService.

    Combines the deterministic decision layer with
    predictive confirmation while preserving the
    MarketService AI contract.
    """

    signal: str
    confidence: float
    score: float

    decision: DecisionAnalysis

    prediction: "PredictionAnalysis | None" = None

    reasons: tuple[str, ...] = ()
    
# =========================================================
# Prediction Analysis
# =========================================================

@dataclass
class PredictionAnalysis:
    """
    NPAT predictive confirmation analysis.

    Combines derivative-market evidence with the broader
    market regime to estimate directional bias.

    This is a deterministic analytical prediction layer,
    not a trained machine-learning model.
    """

    direction: str
    score: float
    confidence: float

    regime_score: float
    futures_score: float
    greeks_score: float
    premium_score: float

    bullish_evidence: int
    bearish_evidence: int
    neutral_evidence: int

    reasons: tuple[str, ...]