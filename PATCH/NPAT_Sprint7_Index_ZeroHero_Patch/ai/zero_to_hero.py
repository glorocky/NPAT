"""NPAT expiry-day Zero-to-Hero option scanner."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
ZERO_HERO_START = time(13, 0)
ZERO_HERO_END = time(13, 30)


@dataclass(frozen=True, slots=True)
class ZeroToHeroCandidate:
    strike_price: int
    option_type: str
    market_premium: float
    score: float
    reason: str


def is_zero_to_hero_window(expiry: str, current_time: datetime | None = None) -> bool:
    try:
        expiry_date = date.fromisoformat(expiry)
    except ValueError:
        return False

    now = current_time or datetime.now(IST)
    if now.tzinfo is None:
        now = now.replace(tzinfo=IST)
    else:
        now = now.astimezone(IST)

    return now.date() == expiry_date and ZERO_HERO_START <= now.time() <= ZERO_HERO_END


def rank_candidates(*, options, atm_strike: int, option_type: str,
                    premium_analysis=None, max_otm_strikes: int = 3):
    option_type = option_type.upper()
    if option_type not in {"CE", "PE"}:
        return None

    premium_map = {}
    for item in premium_analysis or []:
        premium_map[(item.strike_price, item.option_type.upper())] = item

    raw = []
    for option in options:
        strike = int(option.strike_price)
        distance = strike - atm_strike if option_type == "CE" else atm_strike - strike
        if distance < 0:
            continue

        market = float(option.call_ltp if option_type == "CE" else option.put_ltp)
        volume = int(option.call_volume if option_type == "CE" else option.put_volume)
        oi = int(option.call_oi if option_type == "CE" else option.put_oi)
        if market <= 0:
            continue

        premium = premium_map.get((strike, option_type))
        theoretical = float(premium.forward_bs_premium) if premium else 0.0
        value_edge = max(0.0, min(1.0, (theoretical - market) / theoretical)) if theoretical > 0 else 0.0
        raw.append((strike, market, volume, oi, distance, value_edge))

    if not raw:
        return None

    strikes = sorted({x[0] for x in raw})
    spacings = [b - a for a, b in zip(strikes, strikes[1:]) if b > a]
    spacing = min(spacings) if spacings else 1
    max_volume = max(x[2] for x in raw) or 1
    max_oi = max(x[3] for x in raw) or 1

    scored = []
    for strike, market, volume, oi, distance, value_edge in raw:
        steps = round(distance / spacing)
        if steps > max_otm_strikes:
            continue
        distance_score = {0: 10.0, 1: 30.0, 2: 35.0, 3: 25.0}.get(steps, 5.0)
        activity_score = (volume / max_volume) * 25.0 + (oi / max_oi) * 15.0
        affordability_score = max(0.0, 20.0 - min(market, 20.0))
        value_score = value_edge * 30.0
        score = distance_score + activity_score + affordability_score + value_score
        scored.append(
            ZeroToHeroCandidate(
                strike_price=strike,
                option_type=option_type,
                market_premium=market,
                score=round(score, 2),
                reason=(
                    f"Expiry-day zero-to-hero candidate: {option_type} {strike}; "
                    f"LTP ₹{market:.2f}, volume {volume:,}, OI {oi:,}, score {score:.1f}."
                ),
            )
        )

    return max(scored, key=lambda x: x.score) if scored else None
