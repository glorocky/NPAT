from datetime import datetime

import pytest

from ai.option_selector import OptionSelector
from ai.zero_to_hero import is_zero_to_hero_window
from core.models import OptionData


def _option(strike, *, call_ltp=100.0, put_ltp=100.0, call_iv=15.0, put_iv=15.0,
            call_volume=1_000, put_volume=1_000, call_oi=1_000, put_oi=1_000):
    return OptionData(
        strike_price=strike, expiry="2026-08-20", underlying_price=24000.0,
        call_ltp=call_ltp, put_ltp=put_ltp, call_iv=call_iv, put_iv=put_iv,
        call_volume=call_volume, put_volume=put_volume, call_oi=call_oi, put_oi=put_oi,
    )


def _select(signal="BUY", options=None, expiry="2026-08-20", now=None):
    return OptionSelector.select(
        symbol="NIFTY", expiry=expiry, spot_price=24000.0, atm_strike=24000,
        options=options or [_option(24000)], signal=signal, confidence=80.0,
        current_time=now,
    )


def test_bullish_selects_valid_atm_call():
    result = _select("BUY")
    assert (result.action, result.option_type, result.strike_price, result.entry_price) == ("BUY CALL", "CE", 24000, 100.0)


def test_bearish_selects_valid_atm_put():
    result = _select("SELL")
    assert (result.action, result.option_type, result.strike_price, result.entry_price) == ("BUY PUT", "PE", 24000, 100.0)


def test_neutral_returns_no_trade():
    assert _select("NEUTRAL").action == "NO TRADE"


def test_zero_to_hero_uses_ranked_candidate_and_atm_fallback():
    options = [_option(23900), _option(23950), _option(24000), _option(24050, call_volume=10_000), _option(24100)]
    result = _select(options=options, now=datetime(2026, 8, 20, 13, 15))
    assert result.option_type == "CE"
    assert result.strike_price == 24050
    assert "expiry window" in result.reason

    fallback = _select(options=[_option(24000), _option(24050, call_ltp=0.0)], now=datetime(2026, 8, 20, 13, 15))
    assert fallback.strike_price == 24000


@pytest.mark.parametrize("moment", [datetime(2026, 8, 20, 13, 0), datetime(2026, 8, 20, 13, 30)])
def test_zero_to_hero_window_includes_boundaries(moment):
    assert is_zero_to_hero_window("20-Aug-2026", moment)


def test_invalid_expiry_uses_safe_normal_selection():
    result = _select(expiry="not-an-expiry", now=datetime(2026, 8, 20, 13, 15))
    assert result.action == "BUY CALL"
    assert "not recognised" in result.reason


@pytest.mark.parametrize("kwargs", [
    {"call_ltp": 0.0}, {"call_iv": 0.0}, {"call_iv": float("nan")},
    {"call_volume": 99}, {"call_oi": 99},
])
def test_invalid_or_poor_liquidity_call_returns_no_trade(kwargs):
    assert _select(options=[_option(24000, **kwargs)]).action == "NO TRADE"


def test_no_valid_candidate_returns_no_trade_when_atm_is_invalid():
    options = [_option(24000, call_ltp=0.0), _option(24050, call_ltp=0.0)]
    assert _select(options=options, now=datetime(2026, 8, 20, 13, 15)).action == "NO TRADE"


def test_zero_to_hero_tie_breaking_is_deterministic():
    options = [_option(23950), _option(24000), _option(24050), _option(24100)]
    result = _select(options=options, now=datetime(2026, 8, 20, 13, 15))
    assert result.strike_price == 24050
