from core.models import OptionGreeks
from analytics.greeks_analytics import GreeksAnalytics
from providers.exceptions import ProviderDataError
from datetime import datetime, timedelta


# =====================================================
# Controlled Future Expiry
# =====================================================

EXPIRY = (
    datetime.now()
    + timedelta(days=30)
).strftime("%Y-%m-%d")


# =====================================================
# Provider With Valid Greeks
# =====================================================

class ValidGreeksProvider:

    def get_greeks(
        self,
        exchange,
        symbol,
        expiry,
        strike,
        option_type,
    ):
        return OptionGreeks(
            symbol=symbol,
            expiry=expiry,
            strike_price=strike,
            option_type=option_type,
            delta=0.55,
            gamma=0.001,
            theta=-10.0,
            vega=20.0,
            rho=5.0,
            iv=18.0,
        )


valid_result = GreeksAnalytics._get_greeks_with_fallback(
    provider=ValidGreeksProvider(),
    exchange="NSE",
    symbol="NIFTY",
    expiry=EXPIRY,
    strike_price=24000,
    option_type="CE",
    market_price=500.0,
    spot_price=24000.0,
)


assert isinstance(
    valid_result,
    OptionGreeks,
)

assert valid_result.delta == 0.55
assert valid_result.gamma == 0.001
assert valid_result.theta == -10.0
assert valid_result.vega == 20.0
assert valid_result.rho == 5.0
assert valid_result.iv == 18.0


print(
    "Provider Greeks path passed."
)


# =====================================================
# Provider With Missing Greeks
# =====================================================

class MissingGreeksProvider:

    def get_greeks(
        self,
        exchange,
        symbol,
        expiry,
        strike,
        option_type,
    ):
        raise ProviderDataError(
            "Provider get_greeks response contains "
            "incomplete Greeks data."
        )
        
# =====================================================
# Provider IV Fallback
# =====================================================

provider_iv_result = (
    GreeksAnalytics._get_greeks_with_fallback(
        provider=MissingGreeksProvider(),
        exchange="NSE",
        symbol="NIFTY",
        expiry=EXPIRY,
        strike_price=24000,
        option_type="CE",
        market_price=0.0,
        spot_price=24000.0,
        provider_iv=20.0,
    )
)

assert isinstance(
    provider_iv_result,
    OptionGreeks,
)

assert provider_iv_result.symbol == "NIFTY"
assert provider_iv_result.expiry == EXPIRY
assert provider_iv_result.strike_price == 24000
assert provider_iv_result.option_type == "CE"

# Critical assertion:
# provider IV must be used instead of deriving IV from LTP.
assert provider_iv_result.iv == 20.0

assert provider_iv_result.delta > 0.0
assert provider_iv_result.gamma > 0.0
assert provider_iv_result.theta < 0.0
assert provider_iv_result.vega > 0.0
assert provider_iv_result.rho > 0.0

print(
    "Provider IV fallback path passed."
)
    


fallback_result = GreeksAnalytics._get_greeks_with_fallback(
    provider=MissingGreeksProvider(),
    exchange="NSE",
    symbol="NIFTY",
    expiry=EXPIRY,
    strike_price=24000,
    option_type="CE",
    market_price=678.1378415892323,
    spot_price=24000.0,
)


assert isinstance(
    fallback_result,
    OptionGreeks,
)

assert fallback_result.symbol == "NIFTY"
assert fallback_result.expiry == EXPIRY
assert fallback_result.strike_price == 24000
assert fallback_result.option_type == "CE"

assert fallback_result.delta > 0.0
assert fallback_result.gamma > 0.0
assert fallback_result.theta < 0.0
assert fallback_result.vega > 0.0
assert fallback_result.rho > 0.0
assert fallback_result.iv > 0.0


print(
    "Calculated Greeks fallback path passed."
)


# =====================================================
# Unrelated ProviderDataError Must Propagate
# =====================================================

class InvalidProvider:

    def get_greeks(
        self,
        exchange,
        symbol,
        expiry,
        strike,
        option_type,
    ):
        raise ProviderDataError(
            "Unexpected provider payload."
        )


try:

    GreeksAnalytics._get_greeks_with_fallback(
        provider=InvalidProvider(),
        exchange="NSE",
        symbol="NIFTY",
        expiry=EXPIRY,
        strike_price=24000,
        option_type="CE",
        market_price=678.1378415892323,
        spot_price=24000.0,
    )

except ProviderDataError as ex:

    assert (
        str(ex)
        == "Unexpected provider payload."
    )

else:

    raise AssertionError(
        "Unrelated ProviderDataError should "
        "have been re-raised."
    )


print(
    "Provider error propagation passed."
)

print(
    "\nGreeks fallback controlled test passed."
)