"""Expiry-day Zero-to-Hero contract screening utilities."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time
import math
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
ZERO_HERO_START = time(13, 0)
ZERO_HERO_END = time(13, 30)

MIN_OPTION_VOLUME = 100
MIN_OPTION_OI = 100
MAX_OPTION_IV = 500.0


@dataclass(frozen=True, slots=True)
class ZeroToHeroCandidate:
    strike_price: int
    option_type: str
    market_premium: float
    score: float
    reason: str


def parse_expiry_date(expiry: str | date | datetime) -> date | None:
    """Parse known provider expiry formats without raising into the UI."""
    if isinstance(expiry, datetime):
        return expiry.date()
    if isinstance(expiry, date):
        return expiry
    if not isinstance(expiry, str):
        return None

    value = expiry.strip()
    for fmt in ("%Y-%m-%d", "%d-%b-%Y", "%d %b %Y", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def is_zero_to_hero_window(expiry: str | date | datetime,
                           current_time: datetime | None = None) -> bool:
    """Return whether the supplied time is in the expiry-day IST scan window."""
    expiry_date = parse_expiry_date(expiry)
    if expiry_date is None:
        return False

    now = current_time or datetime.now(IST)
    now = now.replace(tzinfo=IST) if now.tzinfo is None else now.astimezone(IST)
    return now.date() == expiry_date and ZERO_HERO_START <= now.time() <= ZERO_HERO_END


def _side_values(option, option_type: str) -> tuple[float, float, int, int]:
    if option_type == "CE":
        return (float(option.call_ltp), float(option.call_iv), int(option.call_volume), int(option.call_oi))
    return (float(option.put_ltp), float(option.put_iv), int(option.put_volume), int(option.put_oi))


def _is_valid_contract(option, option_type: str) -> bool:
    market, iv, volume, oi = _side_values(option, option_type)
    return (
        math.isfinite(market) and market > 0.0
        and math.isfinite(iv) and 0.0 < iv <= MAX_OPTION_IV
        and volume >= MIN_OPTION_VOLUME
        and oi >= MIN_OPTION_OI
    )


def rank_candidates(*, options, atm_strike: int, option_type: str,
                    premium_analysis=None, max_otm_strikes: int = 3):
    """Rank liquid, valid ATM-to-OTM expiry-day contracts deterministically."""
    option_type = option_type.upper()
    if option_type not in {"CE", "PE"} or max_otm_strikes < 0:
        return None

    valid_options = [option for option in options if _is_valid_contract(option, option_type)]
    if not valid_options:
        return None

    strikes = sorted({int(option.strike_price) for option in valid_options})
    spacings = [right - left for left, right in zip(strikes, strikes[1:]) if right > left]
    if not spacings:
        return None
    spacing = min(spacings)

    premium_map = {
        (item.strike_price, item.option_type.upper()): item
        for item in (premium_analysis or [])
    }
    raw = []
    for option in valid_options:
        strike = int(option.strike_price)
        distance = strike - atm_strike if option_type == "CE" else atm_strike - strike
        if distance < 0 or distance % spacing != 0:
            continue
        steps = distance // spacing
        if steps > max_otm_strikes:
            continue
        market, _iv, volume, oi = _side_values(option, option_type)
        premium = premium_map.get((strike, option_type))
        theoretical = float(premium.forward_bs_premium) if premium and premium.forward_bs_premium is not None else None
        value_edge = ((theoretical - market) / theoretical) if theoretical and theoretical > 0.0 else 0.0
        raw.append((strike, market, volume, oi, steps, max(0.0, min(value_edge, 1.0))))

    if not raw:
        return None

    max_volume = max(item[2] for item in raw)
    max_oi = max(item[3] for item in raw)
    candidates = []
    for strike, market, volume, oi, steps, value_edge in raw:
        distance_score = {0: 30.0, 1: 35.0, 2: 30.0, 3: 20.0}.get(steps, 0.0)
        liquidity_score = (volume / max_volume) * 35.0 + (oi / max_oi) * 20.0
        value_score = value_edge * 15.0
        score = distance_score + liquidity_score + value_score
        candidates.append(ZeroToHeroCandidate(
            strike_price=strike,
            option_type=option_type,
            market_premium=market,
            score=round(score, 2),
            reason=(f"Expiry-day candidate: {option_type} {strike}; LTP ₹{market:.2f}, "
                    f"volume {volume:,}, OI {oi:,}, score {score:.1f}."),
        ))

    return max(candidates, key=lambda item: (item.score, -abs(item.strike_price - atm_strike), -item.strike_price))
