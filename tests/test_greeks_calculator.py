from analytics.greeks_calculator import GreeksCalculator
from core.models import OptionGreeks


# =====================================================
# Controlled Inputs
# =====================================================

SPOT_PRICE = 24000.0
STRIKE_PRICE = 24000
TIME_TO_EXPIRY = 0.1
RISK_FREE_RATE = 0.06
VOLATILITY = 0.20


# =====================================================
# Distribution Primitives
# =====================================================

assert GreeksCalculator.normal_cdf(0.0) == 0.5

assert abs(
    GreeksCalculator.normal_pdf(0.0)
    - 0.3989422804014327
) < 1e-12


# =====================================================
# d1 / d2
# =====================================================

d1, d2 = GreeksCalculator.calculate_d1_d2(
    spot_price=SPOT_PRICE,
    strike_price=STRIKE_PRICE,
    time_to_expiry=TIME_TO_EXPIRY,
    risk_free_rate=RISK_FREE_RATE,
    volatility=VOLATILITY,
)

assert abs(
    d1 - 0.12649110640673517
) < 1e-12

assert abs(
    d2 - 0.06324555320336757
) < 1e-12


# =====================================================
# Black-Scholes Premiums
# =====================================================

call_price = GreeksCalculator.black_scholes_price(
    spot_price=SPOT_PRICE,
    strike_price=STRIKE_PRICE,
    time_to_expiry=TIME_TO_EXPIRY,
    risk_free_rate=RISK_FREE_RATE,
    volatility=VOLATILITY,
    option_type="CE",
)

put_price = GreeksCalculator.black_scholes_price(
    spot_price=SPOT_PRICE,
    strike_price=STRIKE_PRICE,
    time_to_expiry=TIME_TO_EXPIRY,
    risk_free_rate=RISK_FREE_RATE,
    volatility=VOLATILITY,
    option_type="PE",
)

assert abs(
    call_price - 678.1378415892323
) < 1e-9

assert abs(
    put_price - 534.5689788836789
) < 1e-9


# =====================================================
# Implied Volatility Round Trip
# =====================================================

call_iv = GreeksCalculator.implied_volatility(
    market_price=call_price,
    spot_price=SPOT_PRICE,
    strike_price=STRIKE_PRICE,
    time_to_expiry=TIME_TO_EXPIRY,
    risk_free_rate=RISK_FREE_RATE,
    option_type="CE",
)

put_iv = GreeksCalculator.implied_volatility(
    market_price=put_price,
    spot_price=SPOT_PRICE,
    strike_price=STRIKE_PRICE,
    time_to_expiry=TIME_TO_EXPIRY,
    risk_free_rate=RISK_FREE_RATE,
    option_type="PE",
)

assert abs(
    call_iv - VOLATILITY
) < 1e-6

assert abs(
    put_iv - VOLATILITY
) < 1e-6


# =====================================================
# Greeks
# =====================================================

call_greeks = GreeksCalculator.calculate_greeks(
    spot_price=SPOT_PRICE,
    strike_price=STRIKE_PRICE,
    time_to_expiry=TIME_TO_EXPIRY,
    risk_free_rate=RISK_FREE_RATE,
    volatility=VOLATILITY,
    option_type="CE",
)

put_greeks = GreeksCalculator.calculate_greeks(
    spot_price=SPOT_PRICE,
    strike_price=STRIKE_PRICE,
    time_to_expiry=TIME_TO_EXPIRY,
    risk_free_rate=RISK_FREE_RATE,
    volatility=VOLATILITY,
    option_type="PE",
)

assert call_greeks["delta"] > 0.0
assert put_greeks["delta"] < 0.0

assert abs(
    call_greeks["gamma"]
    - put_greeks["gamma"]
) < 1e-12

assert abs(
    call_greeks["vega"]
    - put_greeks["vega"]
) < 1e-12

assert call_greeks["theta"] < 0.0
assert put_greeks["theta"] < 0.0

assert call_greeks["rho"] > 0.0
assert put_greeks["rho"] < 0.0

assert call_greeks["iv"] == 20.0
assert put_greeks["iv"] == 20.0


# =====================================================
# NPAT OptionGreeks Model
# =====================================================

normalized = GreeksCalculator.build_option_greeks(
    symbol="NIFTY",
    expiry="2026-08-04",
    strike_price=STRIKE_PRICE,
    option_type="CE",
    market_price=call_price,
    spot_price=SPOT_PRICE,
    time_to_expiry=TIME_TO_EXPIRY,
    risk_free_rate=RISK_FREE_RATE,
)

assert isinstance(
    normalized,
    OptionGreeks,
)

assert normalized.symbol == "NIFTY"
assert normalized.expiry == "2026-08-04"
assert normalized.strike_price == 24000
assert normalized.option_type == "CE"

assert abs(
    normalized.iv - 20.0
) < 1e-6


# =====================================================
# Output
# =====================================================

print("Call Price :", call_price)
print("Put Price  :", put_price)

print()

print("Call IV    :", call_iv * 100.0)
print("Put IV     :", put_iv * 100.0)

print()

print("Call Delta :", call_greeks["delta"])
print("Put Delta  :", put_greeks["delta"])
print("Gamma      :", call_greeks["gamma"])
print("Vega       :", call_greeks["vega"])

print(
    "\nGreeksCalculator controlled test passed."
)