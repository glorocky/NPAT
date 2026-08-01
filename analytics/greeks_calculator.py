"""
analytics/greeks_calculator.py

Provider-independent Black-Scholes Greeks calculator.

Used as a fallback when a market-data provider does not
supply usable implied volatility or option Greeks.
"""

from __future__ import annotations

import math
from core.models import OptionGreeks


class GreeksCalculator:
    """
    Calculate implied volatility and Black-Scholes Greeks
    from option market data.
    """

    # =====================================================
    # Normal Distribution
    # =====================================================

    @staticmethod
    def normal_cdf(
        value: float,
    ) -> float:
        """
        Standard normal cumulative distribution function.
        """

        return 0.5 * (
            1.0
            + math.erf(
                value / math.sqrt(2.0)
            )
        )

    @staticmethod
    def normal_pdf(
        value: float,
    ) -> float:
        """
        Standard normal probability density function.
        """

        return (
            math.exp(
                -0.5 * value**2
            )
            / math.sqrt(
                2.0 * math.pi
            )
        )
    
    # =====================================================
    # Black-Scholes d1 / d2
    # =====================================================

    @staticmethod
    def calculate_d1_d2(
        spot_price: float,
        strike_price: float,
        time_to_expiry: float,
        risk_free_rate: float,
        volatility: float,
    ) -> tuple[float, float]:
        """
        Calculate the Black-Scholes d1 and d2 values.
        """

        if spot_price <= 0:
            raise ValueError(
                "spot_price must be greater than zero."
            )

        if strike_price <= 0:
            raise ValueError(
                "strike_price must be greater than zero."
            )

        if time_to_expiry <= 0:
            raise ValueError(
                "time_to_expiry must be greater than zero."
            )

        if volatility <= 0:
            raise ValueError(
                "volatility must be greater than zero."
            )

        sqrt_time = math.sqrt(
            time_to_expiry
        )

        d1 = (
            math.log(
                spot_price / strike_price
            )
            + (
                risk_free_rate
                + 0.5 * volatility**2
            )
            * time_to_expiry
        ) / (
            volatility * sqrt_time
        )

        d2 = (
            d1
            - volatility * sqrt_time
        )

        return (
            float(d1),
            float(d2),
        )
        
    # =====================================================
    # Black-Scholes Option Price
    # =====================================================

    @classmethod
    def black_scholes_price(
        cls,
        spot_price: float,
        strike_price: float,
        time_to_expiry: float,
        risk_free_rate: float,
        volatility: float,
        option_type: str,
    ) -> float:
        """
        Calculate theoretical European option premium
        using the Black-Scholes model.
        """

        option_type = option_type.upper()

        if option_type not in {"CE", "PE"}:
            raise ValueError(
                "option_type must be CE or PE."
            )

        if spot_price <= 0:
            raise ValueError(
                "spot_price must be greater than zero."
            )

        if strike_price <= 0:
            raise ValueError(
                "strike_price must be greater than zero."
            )

        # -------------------------------------------------
        # Expired Option
        # -------------------------------------------------

        if time_to_expiry <= 0:

            if option_type == "CE":
                return max(
                    spot_price - strike_price,
                    0.0,
                )

            return max(
                strike_price - spot_price,
                0.0,
            )

        # -------------------------------------------------
        # Zero Volatility
        # -------------------------------------------------

        if volatility <= 0:

            discount_factor = math.exp(
                -risk_free_rate * time_to_expiry
            )

            if option_type == "CE":
                return max(
                    spot_price
                    - strike_price * discount_factor,
                    0.0,
                )

            return max(
                strike_price * discount_factor
                - spot_price,
                0.0,
            )

        d1, d2 = cls.calculate_d1_d2(
            spot_price=spot_price,
            strike_price=strike_price,
            time_to_expiry=time_to_expiry,
            risk_free_rate=risk_free_rate,
            volatility=volatility,
        )

        discount_factor = math.exp(
            -risk_free_rate * time_to_expiry
        )

        if option_type == "CE":

            price = (
                spot_price
                * cls.normal_cdf(d1)
                - strike_price
                * discount_factor
                * cls.normal_cdf(d2)
            )

        else:

            price = (
                strike_price
                * discount_factor
                * cls.normal_cdf(-d2)
                - spot_price
                * cls.normal_cdf(-d1)
            )

        return max(
            float(price),
            0.0,
        )
        
    # =====================================================
    # Implied Volatility
    # =====================================================

    @classmethod
    def implied_volatility(
        cls,
        market_price: float,
        spot_price: float,
        strike_price: float,
        time_to_expiry: float,
        risk_free_rate: float,
        option_type: str,
        tolerance: float = 1e-6,
        max_iterations: int = 100,
    ) -> float:
        """
        Estimate annualized implied volatility using
        bisection against the Black-Scholes price.

        Returns volatility as a decimal:
            0.20 = 20% IV
        """

        option_type = option_type.upper()

        if option_type not in {"CE", "PE"}:
            raise ValueError(
                "option_type must be CE or PE."
            )

        if market_price <= 0:
            raise ValueError(
                "market_price must be greater than zero."
            )

        if spot_price <= 0:
            raise ValueError(
                "spot_price must be greater than zero."
            )

        if strike_price <= 0:
            raise ValueError(
                "strike_price must be greater than zero."
            )

        if time_to_expiry <= 0:
            raise ValueError(
                "time_to_expiry must be greater than zero."
            )

        if tolerance <= 0:
            raise ValueError(
                "tolerance must be greater than zero."
            )

        if max_iterations <= 0:
            raise ValueError(
                "max_iterations must be greater than zero."
            )

        # -------------------------------------------------
        # Arbitrage Bounds
        # -------------------------------------------------

        discount_factor = math.exp(
            -risk_free_rate * time_to_expiry
        )

        if option_type == "CE":

            lower_bound = max(
                spot_price
                - strike_price * discount_factor,
                0.0,
            )

            upper_bound = spot_price

        else:

            lower_bound = max(
                strike_price * discount_factor
                - spot_price,
                0.0,
            )

            upper_bound = (
                strike_price * discount_factor
            )

        if (
            market_price < lower_bound - tolerance
            or market_price > upper_bound + tolerance
        ):
            raise ValueError(
                "market_price violates Black-Scholes "
                "arbitrage bounds."
            )

        # -------------------------------------------------
        # Bisection Bounds
        # -------------------------------------------------

        low_volatility = 1e-6
        high_volatility = 5.0

        low_price = cls.black_scholes_price(
            spot_price=spot_price,
            strike_price=strike_price,
            time_to_expiry=time_to_expiry,
            risk_free_rate=risk_free_rate,
            volatility=low_volatility,
            option_type=option_type,
        )

        high_price = cls.black_scholes_price(
            spot_price=spot_price,
            strike_price=strike_price,
            time_to_expiry=time_to_expiry,
            risk_free_rate=risk_free_rate,
            volatility=high_volatility,
            option_type=option_type,
        )

        if market_price < low_price - tolerance:
            raise ValueError(
                "market_price is below the supported "
                "Black-Scholes volatility range."
            )

        if market_price > high_price + tolerance:
            raise ValueError(
                "market_price is above the supported "
                "Black-Scholes volatility range."
            )

        # -------------------------------------------------
        # Bisection
        # -------------------------------------------------

        for _ in range(max_iterations):

            volatility = (
                low_volatility
                + high_volatility
            ) / 2.0

            theoretical_price = (
                cls.black_scholes_price(
                    spot_price=spot_price,
                    strike_price=strike_price,
                    time_to_expiry=time_to_expiry,
                    risk_free_rate=risk_free_rate,
                    volatility=volatility,
                    option_type=option_type,
                )
            )

            difference = (
                theoretical_price
                - market_price
            )

            if abs(difference) <= tolerance:
                return float(volatility)

            if difference > 0:
                high_volatility = volatility
            else:
                low_volatility = volatility

        return float(
            (
                low_volatility
                + high_volatility
            )
            / 2.0
        )
        
        
    # =====================================================
    # Black-Scholes Greeks
    # =====================================================

    @classmethod
    def calculate_greeks(
        cls,
        spot_price: float,
        strike_price: float,
        time_to_expiry: float,
        risk_free_rate: float,
        volatility: float,
        option_type: str,
    ) -> dict[str, float]:
        """
        Calculate Black-Scholes option Greeks.

        Conventions:
        - Delta: standard decimal delta
        - Gamma: change in delta per 1-point move
        - Theta: option-price change per calendar day
        - Vega: option-price change per 1 percentage-point IV move
        - Rho: option-price change per 1 percentage-point rate move
        """

        option_type = option_type.upper()

        if option_type not in {"CE", "PE"}:
            raise ValueError(
                "option_type must be CE or PE."
            )

        if spot_price <= 0:
            raise ValueError(
                "spot_price must be greater than zero."
            )

        if strike_price <= 0:
            raise ValueError(
                "strike_price must be greater than zero."
            )

        if time_to_expiry <= 0:
            raise ValueError(
                "time_to_expiry must be greater than zero."
            )

        if volatility <= 0:
            raise ValueError(
                "volatility must be greater than zero."
            )

        # -------------------------------------------------
        # Shared Values
        # -------------------------------------------------

        d1, d2 = cls.calculate_d1_d2(
            spot_price=spot_price,
            strike_price=strike_price,
            time_to_expiry=time_to_expiry,
            risk_free_rate=risk_free_rate,
            volatility=volatility,
        )

        sqrt_time = math.sqrt(
            time_to_expiry
        )

        discount_factor = math.exp(
            -risk_free_rate * time_to_expiry
        )

        pdf_d1 = cls.normal_pdf(
            d1
        )

        # -------------------------------------------------
        # Delta
        # -------------------------------------------------

        if option_type == "CE":
            delta = cls.normal_cdf(
                d1
            )
        else:
            delta = (
                cls.normal_cdf(d1)
                - 1.0
            )

        # -------------------------------------------------
        # Gamma
        # -------------------------------------------------

        gamma = (
            pdf_d1
            / (
                spot_price
                * volatility
                * sqrt_time
            )
        )

        # -------------------------------------------------
        # Theta
        # -------------------------------------------------

        theta_common = (
            -spot_price
            * pdf_d1
            * volatility
            / (
                2.0
                * sqrt_time
            )
        )

        if option_type == "CE":

            theta_annual = (
                theta_common
                - risk_free_rate
                * strike_price
                * discount_factor
                * cls.normal_cdf(d2)
            )

        else:

            theta_annual = (
                theta_common
                + risk_free_rate
                * strike_price
                * discount_factor
                * cls.normal_cdf(-d2)
            )

        theta = (
            theta_annual
            / 365.0
        )

        # -------------------------------------------------
        # Vega
        # -------------------------------------------------

        vega = (
            spot_price
            * pdf_d1
            * sqrt_time
            / 100.0
        )

        # -------------------------------------------------
        # Rho
        # -------------------------------------------------

        if option_type == "CE":

            rho = (
                strike_price
                * time_to_expiry
                * discount_factor
                * cls.normal_cdf(d2)
                / 100.0
            )

        else:

            rho = (
                -strike_price
                * time_to_expiry
                * discount_factor
                * cls.normal_cdf(-d2)
                / 100.0
            )

        return {
            "delta": float(delta),
            "gamma": float(gamma),
            "theta": float(theta),
            "vega": float(vega),
            "rho": float(rho),
            "iv": float(volatility * 100.0),
        }
        
    # =====================================================
    # Market-Implied Greeks
    # =====================================================

    @classmethod
    def calculate_from_market_price(
        cls,
        market_price: float,
        spot_price: float,
        strike_price: float,
        time_to_expiry: float,
        risk_free_rate: float,
        option_type: str,
    ) -> dict[str, float]:
        """
        Derive implied volatility from the observed option
        premium and calculate the corresponding
        Black-Scholes Greeks.
        """

        volatility = cls.implied_volatility(
            market_price=market_price,
            spot_price=spot_price,
            strike_price=strike_price,
            time_to_expiry=time_to_expiry,
            risk_free_rate=risk_free_rate,
            option_type=option_type,
        )

        return cls.calculate_greeks(
            spot_price=spot_price,
            strike_price=strike_price,
            time_to_expiry=time_to_expiry,
            risk_free_rate=risk_free_rate,
            volatility=volatility,
            option_type=option_type,
        )
        
        # =====================================================
    # NPAT OptionGreeks Model
    # =====================================================

    @classmethod
    def build_option_greeks(
        cls,
        symbol: str,
        expiry: str,
        strike_price: int,
        option_type: str,
        market_price: float,
        spot_price: float,
        time_to_expiry: float,
        risk_free_rate: float,
    ) -> OptionGreeks:
        """
        Derive market-implied Greeks and return them in
        NPAT's normalized OptionGreeks model.
        """

        if not symbol:
            raise ValueError(
                "symbol is required."
            )

        if not expiry:
            raise ValueError(
                "expiry is required."
            )

        option_type = option_type.upper()

        values = cls.calculate_from_market_price(
            market_price=market_price,
            spot_price=spot_price,
            strike_price=float(strike_price),
            time_to_expiry=time_to_expiry,
            risk_free_rate=risk_free_rate,
            option_type=option_type,
        )

        return OptionGreeks(
            symbol=symbol,
            expiry=expiry,
            strike_price=int(strike_price),
            option_type=option_type,

            delta=values["delta"],
            gamma=values["gamma"],
            theta=values["theta"],
            vega=values["vega"],
            rho=values["rho"],
            iv=values["iv"],
        )