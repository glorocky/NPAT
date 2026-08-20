import math

import pytest

from analytics.premium_analytics import PremiumAnalytics


def test_black_scholes_calculates_finite_call_and_put_prices():
    call = PremiumAnalytics.black_scholes_price(24000, 24000, 7 / 365, 0.07, 0.15, "CE")
    put = PremiumAnalytics.black_scholes_price(24000, 24000, 7 / 365, 0.07, 0.15, "PE")
    assert call > 0 and put > 0
    assert math.isfinite(call) and math.isfinite(put)


def test_black_scholes_rejects_invalid_pricing_inputs():
    with pytest.raises(ValueError, match="spot_price"):
        PremiumAnalytics.black_scholes_price(0, 24000, 7 / 365, 0.07, 0.15, "CE")
