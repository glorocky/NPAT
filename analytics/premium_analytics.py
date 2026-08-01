"""
=========================================================
NPAT - Premium Analytics
=========================================================

Purpose
-------
Provider-independent option premium analytics.

Responsibilities
----------------
- Black-Scholes theoretical option pricing
- ATM ± N strike selection
- CE and PE premium analysis
- Market vs theoretical premium comparison
- Moneyness classification

Provider-specific logic must NOT be added here.

Version : 1.0.0
=========================================================
"""

from __future__ import annotations

import math
from datetime import datetime

from core.models import (
    ForwardPremiumAnalysis,
    OptionData,
    ParityAnalysis,
    PremiumAnalysis,
)


class PremiumAnalytics:
    """
    Provider-independent option premium analytics engine.
    """

    # =====================================================
    # Normal Distribution
    # =====================================================

    @staticmethod
    def _normal_cdf(value: float) -> float:
        """
        Standard normal cumulative distribution function.
        """

        return 0.5 * (
            1.0
            + math.erf(
                value / math.sqrt(2.0)
            )
        )

    # =====================================================
    # Black-Scholes
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

        # Expired option or zero volatility.
        if time_to_expiry <= 0 or volatility <= 0:

            if option_type == "CE":
                return max(
                    spot_price - strike_price,
                    0.0,
                )

            return max(
                strike_price - spot_price,
                0.0,
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

        discount_factor = math.exp(
            -risk_free_rate * time_to_expiry
        )

        if option_type == "CE":

            price = (
                spot_price
                * cls._normal_cdf(d1)
                - strike_price
                * discount_factor
                * cls._normal_cdf(d2)
            )

        else:

            price = (
                strike_price
                * discount_factor
                * cls._normal_cdf(-d2)
                - spot_price
                * cls._normal_cdf(-d1)
            )

        return max(
            float(price),
            0.0,
        )

    # =====================================================
    # Time To Expiry
    # =====================================================

    @staticmethod
    def calculate_time_to_expiry(
        expiry: str,
        current_time: datetime | None = None,
    ) -> float:
        """
        Calculate remaining time to expiry in years.

        NSE option expiry time is treated as 15:30.
        """

        now = (
            current_time
            if current_time is not None
            else datetime.now()
        )

        expiry_date = datetime.strptime(
            expiry,
            "%Y-%m-%d",
        )

        expiry_time = expiry_date.replace(
            hour=15,
            minute=30,
            second=0,
            microsecond=0,
        )

        remaining_seconds = (
            expiry_time - now
        ).total_seconds()

        if remaining_seconds <= 0:
            return 0.0

        seconds_per_year = (
            365.0
            * 24.0
            * 60.0
            * 60.0
        )

        return (
            remaining_seconds
            / seconds_per_year
        )

    # =====================================================
    # Moneyness
    # =====================================================

    @staticmethod
    def determine_moneyness(
        spot_price: float,
        strike_price: int,
        option_type: str,
        atm_strike: int,
    ) -> str:
        """
        Determine whether the option is ATM, ITM or OTM.
        """

        option_type = option_type.upper()

        if option_type not in {"CE", "PE"}:
            raise ValueError(
                "option_type must be CE or PE."
            )

        if strike_price == atm_strike:
            return "ATM"

        if option_type == "CE":

            if strike_price < spot_price:
                return "ITM"

            return "OTM"

        if strike_price > spot_price:
            return "ITM"

        return "OTM"

    # =====================================================
    # ATM Window
    # =====================================================

    @staticmethod
    def select_atm_window(
        options: list[OptionData],
        atm_strike: int,
        strikes_each_side: int = 3,
    ) -> list[OptionData]:
        """
        Select ATM plus N available strikes on either side.
        """

        if not options:
            raise ValueError(
                "Option chain cannot be empty."
            )

        if strikes_each_side < 0:
            raise ValueError(
                "strikes_each_side cannot be negative."
            )

        sorted_options = sorted(
            options,
            key=lambda option: option.strike_price,
        )

        atm_index = next(
            (
                index
                for index, option
                in enumerate(sorted_options)
                if option.strike_price == atm_strike
            ),
            None,
        )

        if atm_index is None:
            raise ValueError(
                f"ATM strike {atm_strike} "
                "does not exist in option chain."
            )

        start_index = max(
            atm_index - strikes_each_side,
            0,
        )

        end_index = min(
            atm_index + strikes_each_side + 1,
            len(sorted_options),
        )

        return sorted_options[
            start_index:end_index
        ]

    # =====================================================
    # Premium Difference
    # =====================================================

    @staticmethod
    def _premium_difference(
        market_premium: float,
        theoretical_premium: float,
    ) -> tuple[float, float]:
        """
        Calculate market premium minus theoretical premium.

        Positive:
            Market premium is above theoretical premium.

        Negative:
            Market premium is below theoretical premium.
        """

        difference = (
            market_premium
            - theoretical_premium
        )

        if theoretical_premium <= 0:
            difference_pct = 0.0

        else:
            difference_pct = (
                difference
                / theoretical_premium
                * 100.0
            )

        return (
            difference,
            difference_pct,
        )

    # =====================================================
    # Analyze ATM Window
    # =====================================================

    @classmethod
    def analyze_atm_window(
        cls,
        symbol: str,
        options: list[OptionData],
        atm_strike: int,
        expiry: str,
        risk_free_rate: float,
        strikes_each_side: int = 3,
        current_time: datetime | None = None,
    ) -> list[PremiumAnalysis]:
        """
        Analyze CE and PE premiums for ATM ± N strikes.

        ATM ±3 produces:

        7 strikes
        ×
        CE + PE
        =
        14 PremiumAnalysis objects
        """

        if not symbol:
            raise ValueError(
                "symbol is required."
            )

        if not options:
            raise ValueError(
                "Option chain cannot be empty."
            )

        selected_options = cls.select_atm_window(
            options=options,
            atm_strike=atm_strike,
            strikes_each_side=strikes_each_side,
        )

        time_to_expiry = cls.calculate_time_to_expiry(
            expiry=expiry,
            current_time=current_time,
        )

        results: list[PremiumAnalysis] = []

        for option in selected_options:

            spot_price = float(
                option.underlying_price
            )

            # =================================================
            # CALL
            # =================================================

            call_iv = max(
                float(option.call_iv),
                0.0,
            )

            call_theoretical = cls.black_scholes_price(
                spot_price=spot_price,
                strike_price=float(
                    option.strike_price
                ),
                time_to_expiry=time_to_expiry,
                risk_free_rate=risk_free_rate,
                volatility=call_iv / 100.0,
                option_type="CE",
            )

            (
                call_difference,
                call_difference_pct,
            ) = cls._premium_difference(
                market_premium=float(
                    option.call_ltp
                ),
                theoretical_premium=call_theoretical,
            )

            results.append(
                PremiumAnalysis(
                    symbol=symbol,
                    expiry=expiry,
                    strike_price=option.strike_price,
                    option_type="CE",
                    underlying_price=spot_price,

                    market_premium=float(
                        option.call_ltp
                    ),

                    theoretical_premium=(
                        call_theoretical
                    ),

                    premium_difference=(
                        call_difference
                    ),

                    premium_difference_pct=(
                        call_difference_pct
                    ),

                    iv=call_iv,

                    moneyness=cls.determine_moneyness(
                        spot_price=spot_price,
                        strike_price=option.strike_price,
                        option_type="CE",
                        atm_strike=atm_strike,
                    ),

                    time_to_expiry=time_to_expiry,
                )
            )

            # =================================================
            # PUT
            # =================================================

            put_iv = max(
                float(option.put_iv),
                0.0,
            )

            put_theoretical = cls.black_scholes_price(
                spot_price=spot_price,
                strike_price=float(
                    option.strike_price
                ),
                time_to_expiry=time_to_expiry,
                risk_free_rate=risk_free_rate,
                volatility=put_iv / 100.0,
                option_type="PE",
            )

            (
                put_difference,
                put_difference_pct,
            ) = cls._premium_difference(
                market_premium=float(
                    option.put_ltp
                ),
                theoretical_premium=put_theoretical,
            )

            results.append(
                PremiumAnalysis(
                    symbol=symbol,
                    expiry=expiry,
                    strike_price=option.strike_price,
                    option_type="PE",
                    underlying_price=spot_price,

                    market_premium=float(
                        option.put_ltp
                    ),

                    theoretical_premium=(
                        put_theoretical
                    ),

                    premium_difference=(
                        put_difference
                    ),

                    premium_difference_pct=(
                        put_difference_pct
                    ),

                    iv=put_iv,

                    moneyness=cls.determine_moneyness(
                        spot_price=spot_price,
                        strike_price=option.strike_price,
                        option_type="PE",
                        atm_strike=atm_strike,
                    ),

                    time_to_expiry=time_to_expiry,
                )
            )

        return results
    # =====================================================
    # Implied Forward
    # =====================================================

    @staticmethod
    def calculate_implied_forward(
        strike_price: float,
        call_premium: float,
        put_premium: float,
        risk_free_rate: float,
        time_to_expiry: float,
    ) -> float:
        """
        Calculate implied forward from put-call parity.

        F = K + (C - P) * exp(rT)
        """

        if strike_price <= 0:
            raise ValueError(
                "strike_price must be greater than zero."
            )

        growth_factor = math.exp(
            risk_free_rate * time_to_expiry
        )

        return (
            strike_price
            + (
                call_premium
                - put_premium
            )
            * growth_factor
        )

    # =====================================================
    # Put-Call Parity
    # =====================================================

    @classmethod
    def analyze_put_call_parity(
        cls,
        symbol: str,
        options: list[OptionData],
        atm_strike: int,
        expiry: str,
        risk_free_rate: float,
        strikes_each_side: int = 3,
        current_time: datetime | None = None,
    ) -> list[ParityAnalysis]:
        """
        Analyze put-call parity for ATM ± N strikes.

        Uses:

        C - P = S - K * exp(-rT)

        and derives the implied forward:

        F = K + (C - P) * exp(rT)
        """

        if not symbol:
            raise ValueError(
                "symbol is required."
            )

        if not options:
            raise ValueError(
                "Option chain cannot be empty."
            )

        selected_options = cls.select_atm_window(
            options=options,
            atm_strike=atm_strike,
            strikes_each_side=strikes_each_side,
        )

        time_to_expiry = cls.calculate_time_to_expiry(
            expiry=expiry,
            current_time=current_time,
        )

        discount_factor = math.exp(
            -risk_free_rate * time_to_expiry
        )

        results: list[ParityAnalysis] = []

        for option in selected_options:

            spot_price = float(
                option.underlying_price
            )

            strike_price = float(
                option.strike_price
            )

            call_premium = float(
                option.call_ltp
            )

            put_premium = float(
                option.put_ltp
            )

            # ---------------------------------------------
            # Market parity
            # ---------------------------------------------

            market_parity = (
                call_premium
                - put_premium
            )

            # ---------------------------------------------
            # Theoretical parity
            # ---------------------------------------------

            theoretical_parity = (
                spot_price
                - strike_price
                * discount_factor
            )

            parity_deviation = (
                market_parity
                - theoretical_parity
            )

            if abs(theoretical_parity) > 1e-12:

                parity_deviation_pct = (
                    parity_deviation
                    / abs(theoretical_parity)
                    * 100.0
                )

            else:

                parity_deviation_pct = 0.0

            # ---------------------------------------------
            # Implied Forward
            # ---------------------------------------------

            implied_forward = (
                cls.calculate_implied_forward(
                    strike_price=strike_price,
                    call_premium=call_premium,
                    put_premium=put_premium,
                    risk_free_rate=risk_free_rate,
                    time_to_expiry=time_to_expiry,
                )
            )

            forward_premium = (
                implied_forward
                - spot_price
            )

            if spot_price > 0:

                forward_premium_pct = (
                    forward_premium
                    / spot_price
                    * 100.0
                )

            else:

                forward_premium_pct = 0.0

            results.append(
                ParityAnalysis(
                    symbol=symbol,
                    expiry=expiry,
                    strike_price=option.strike_price,
                    spot_price=spot_price,

                    call_premium=call_premium,
                    put_premium=put_premium,

                    implied_forward=implied_forward,
                    forward_premium=forward_premium,
                    forward_premium_pct=forward_premium_pct,

                    market_parity=market_parity,
                    theoretical_parity=theoretical_parity,
                    parity_deviation=parity_deviation,
                    parity_deviation_pct=parity_deviation_pct,

                    time_to_expiry=time_to_expiry,
                )
            )

        return results
    
    # =====================================================
    # Forward Black-Scholes
    # =====================================================

    @classmethod
    def forward_black_scholes_price(
        cls,
        forward_price: float,
        strike_price: float,
        time_to_expiry: float,
        risk_free_rate: float,
        volatility: float,
        option_type: str,
    ) -> float:
        """
        Calculate theoretical option premium using the
        forward form of Black-Scholes.

        Call:
            exp(-rT) * [F*N(d1) - K*N(d2)]

        Put:
            exp(-rT) * [K*N(-d2) - F*N(-d1)]
        """

        option_type = option_type.upper()

        if option_type not in {"CE", "PE"}:
            raise ValueError(
                "option_type must be CE or PE."
            )

        if forward_price <= 0:
            raise ValueError(
                "forward_price must be greater than zero."
            )

        if strike_price <= 0:
            raise ValueError(
                "strike_price must be greater than zero."
            )

        discount_factor = math.exp(
            -risk_free_rate * max(
                time_to_expiry,
                0.0,
            )
        )

        # ---------------------------------------------
        # Expiry / Zero Volatility
        # ---------------------------------------------

        if time_to_expiry <= 0 or volatility <= 0:

            if option_type == "CE":

                return (
                    discount_factor
                    * max(
                        forward_price - strike_price,
                        0.0,
                    )
                )

            return (
                discount_factor
                * max(
                    strike_price - forward_price,
                    0.0,
                )
            )

        sqrt_time = math.sqrt(
            time_to_expiry
        )

        d1 = (
            math.log(
                forward_price / strike_price
            )
            + 0.5 * volatility**2
            * time_to_expiry
        ) / (
            volatility * sqrt_time
        )

        d2 = (
            d1
            - volatility * sqrt_time
        )

        if option_type == "CE":

            price = (
                discount_factor
                * (
                    forward_price
                    * cls._normal_cdf(d1)
                    - strike_price
                    * cls._normal_cdf(d2)
                )
            )

        else:

            price = (
                discount_factor
                * (
                    strike_price
                    * cls._normal_cdf(-d2)
                    - forward_price
                    * cls._normal_cdf(-d1)
                )
            )

        return max(
            float(price),
            0.0,
        )
        
    # =====================================================
    # Forward-Aware Premium Analysis
    # =====================================================

    @classmethod
    def analyze_forward_premiums(
        cls,
        symbol: str,
        options: list[OptionData],
        atm_strike: int,
        expiry: str,
        risk_free_rate: float,
        strikes_each_side: int = 3,
        current_time: datetime | None = None,
    ) -> list[ForwardPremiumAnalysis]:
        """
        Compare market premium against:

        1. Spot-based Black-Scholes
        2. Forward-aware Black-Scholes

        The implied forward is derived independently for
        each strike from that strike's CE and PE premiums.
        """

        if not symbol:
            raise ValueError(
                "symbol is required."
            )

        if not options:
            raise ValueError(
                "Option chain cannot be empty."
            )

        selected_options = cls.select_atm_window(
            options=options,
            atm_strike=atm_strike,
            strikes_each_side=strikes_each_side,
        )

        time_to_expiry = cls.calculate_time_to_expiry(
            expiry=expiry,
            current_time=current_time,
        )

        results: list[ForwardPremiumAnalysis] = []

        for option in selected_options:

            spot_price = float(
                option.underlying_price
            )

            strike_price = float(
                option.strike_price
            )

            call_market = float(
                option.call_ltp
            )

            put_market = float(
                option.put_ltp
            )

            # ---------------------------------------------
            # Implied Forward
            # ---------------------------------------------

            implied_forward = (
                cls.calculate_implied_forward(
                    strike_price=strike_price,
                    call_premium=call_market,
                    put_premium=put_market,
                    risk_free_rate=risk_free_rate,
                    time_to_expiry=time_to_expiry,
                )
            )

            # =============================================
            # CALL
            # =============================================

            call_iv = max(
                float(option.call_iv),
                0.0,
            )

            call_volatility = (
                call_iv / 100.0
            )

            call_spot_bs = cls.black_scholes_price(
                spot_price=spot_price,
                strike_price=strike_price,
                time_to_expiry=time_to_expiry,
                risk_free_rate=risk_free_rate,
                volatility=call_volatility,
                option_type="CE",
            )

            call_forward_bs = (
                cls.forward_black_scholes_price(
                    forward_price=implied_forward,
                    strike_price=strike_price,
                    time_to_expiry=time_to_expiry,
                    risk_free_rate=risk_free_rate,
                    volatility=call_volatility,
                    option_type="CE",
                )
            )

            (
                call_spot_difference,
                call_spot_difference_pct,
            ) = cls._premium_difference(
                market_premium=call_market,
                theoretical_premium=call_spot_bs,
            )

            (
                call_forward_difference,
                call_forward_difference_pct,
            ) = cls._premium_difference(
                market_premium=call_market,
                theoretical_premium=call_forward_bs,
            )

            results.append(
                ForwardPremiumAnalysis(
                    symbol=symbol,
                    expiry=expiry,
                    strike_price=option.strike_price,
                    option_type="CE",

                    spot_price=spot_price,
                    implied_forward=implied_forward,

                    market_premium=call_market,

                    spot_bs_premium=call_spot_bs,
                    forward_bs_premium=call_forward_bs,

                    spot_difference=call_spot_difference,
                    spot_difference_pct=(
                        call_spot_difference_pct
                    ),

                    forward_difference=(
                        call_forward_difference
                    ),
                    forward_difference_pct=(
                        call_forward_difference_pct
                    ),

                    iv=call_iv,
                    time_to_expiry=time_to_expiry,

                    moneyness=cls.determine_moneyness(
                        spot_price=spot_price,
                        strike_price=option.strike_price,
                        option_type="CE",
                        atm_strike=atm_strike,
                    ),
                )
            )

            # =============================================
            # PUT
            # =============================================

            put_iv = max(
                float(option.put_iv),
                0.0,
            )

            put_volatility = (
                put_iv / 100.0
            )

            put_spot_bs = cls.black_scholes_price(
                spot_price=spot_price,
                strike_price=strike_price,
                time_to_expiry=time_to_expiry,
                risk_free_rate=risk_free_rate,
                volatility=put_volatility,
                option_type="PE",
            )

            put_forward_bs = (
                cls.forward_black_scholes_price(
                    forward_price=implied_forward,
                    strike_price=strike_price,
                    time_to_expiry=time_to_expiry,
                    risk_free_rate=risk_free_rate,
                    volatility=put_volatility,
                    option_type="PE",
                )
            )

            (
                put_spot_difference,
                put_spot_difference_pct,
            ) = cls._premium_difference(
                market_premium=put_market,
                theoretical_premium=put_spot_bs,
            )

            (
                put_forward_difference,
                put_forward_difference_pct,
            ) = cls._premium_difference(
                market_premium=put_market,
                theoretical_premium=put_forward_bs,
            )

            results.append(
                ForwardPremiumAnalysis(
                    symbol=symbol,
                    expiry=expiry,
                    strike_price=option.strike_price,
                    option_type="PE",

                    spot_price=spot_price,
                    implied_forward=implied_forward,

                    market_premium=put_market,

                    spot_bs_premium=put_spot_bs,
                    forward_bs_premium=put_forward_bs,

                    spot_difference=put_spot_difference,
                    spot_difference_pct=(
                        put_spot_difference_pct
                    ),

                    forward_difference=(
                        put_forward_difference
                    ),
                    forward_difference_pct=(
                        put_forward_difference_pct
                    ),

                    iv=put_iv,
                    time_to_expiry=time_to_expiry,

                    moneyness=cls.determine_moneyness(
                        spot_price=spot_price,
                        strike_price=option.strike_price,
                        option_type="PE",
                        atm_strike=atm_strike,
                    ),
                )
            )

        return results
    
    # =====================================================
    # Robust Common Forward
    # =====================================================

    @classmethod
    def calculate_common_forward(
        cls,
        options: list[OptionData],
        atm_strike: int,
        risk_free_rate: float,
        time_to_expiry: float,
        strikes_each_side: int = 3,
    ) -> float:
        """
        Calculate one representative implied forward from
        ATM ± N option pairs.

        Uses the median rather than the arithmetic mean so
        one abnormal strike cannot distort the result.
        """

        if not options:
            raise ValueError(
                "Option chain cannot be empty."
            )

        selected_options = cls.select_atm_window(
            options=options,
            atm_strike=atm_strike,
            strikes_each_side=strikes_each_side,
        )

        implied_forwards: list[float] = []

        for option in selected_options:

            call_premium = float(
                option.call_ltp
            )

            put_premium = float(
                option.put_ltp
            )

            implied_forward = (
                cls.calculate_implied_forward(
                    strike_price=float(
                        option.strike_price
                    ),
                    call_premium=call_premium,
                    put_premium=put_premium,
                    risk_free_rate=risk_free_rate,
                    time_to_expiry=time_to_expiry,
                )
            )

            if math.isfinite(implied_forward):
                implied_forwards.append(
                    implied_forward
                )

        if not implied_forwards:
            raise ValueError(
                "Unable to calculate common forward."
            )

        implied_forwards.sort()

        count = len(
            implied_forwards
        )

        middle = count // 2

        if count % 2 == 1:
            common_forward = (
                implied_forwards[middle]
            )

        else:
            common_forward = (
                implied_forwards[middle - 1]
                + implied_forwards[middle]
            ) / 2.0

        return float(
            common_forward
        )
        
    # =====================================================
    # Common-Forward Premium Analysis
    # =====================================================

    @classmethod
    def analyze_common_forward_premiums(
        cls,
        symbol: str,
        options: list[OptionData],
        atm_strike: int,
        expiry: str,
        risk_free_rate: float,
        strikes_each_side: int = 3,
        current_time: datetime | None = None,
    ) -> list[ForwardPremiumAnalysis]:
        """
        Analyze ATM ±N option premiums using one robust
        common implied forward for every selected contract.

        This avoids deriving each contract's pricing forward
        from that same strike's CE/PE pair.
        """

        if not symbol:
            raise ValueError(
                "symbol is required."
            )

        if not options:
            raise ValueError(
                "Option chain cannot be empty."
            )

        # -------------------------------------------------
        # Time To Expiry
        # -------------------------------------------------

        time_to_expiry = cls.calculate_time_to_expiry(
            expiry=expiry,
            current_time=current_time,
        )

        # -------------------------------------------------
        # Common Forward
        # -------------------------------------------------

        common_forward = cls.calculate_common_forward(
            options=options,
            atm_strike=atm_strike,
            risk_free_rate=risk_free_rate,
            time_to_expiry=time_to_expiry,
            strikes_each_side=strikes_each_side,
        )

        # -------------------------------------------------
        # ATM Window
        # -------------------------------------------------

        selected_options = cls.select_atm_window(
            options=options,
            atm_strike=atm_strike,
            strikes_each_side=strikes_each_side,
        )

        results: list[ForwardPremiumAnalysis] = []

        for option in selected_options:

            spot_price = float(
                option.underlying_price
            )

            strike_price = float(
                option.strike_price
            )

            # =================================================
            # CALL
            # =================================================

            call_market = float(
                option.call_ltp
            )

            call_iv = max(
                float(option.call_iv),
                0.0,
            )

            call_volatility = (
                call_iv / 100.0
            )

            call_spot_bs = cls.black_scholes_price(
                spot_price=spot_price,
                strike_price=strike_price,
                time_to_expiry=time_to_expiry,
                risk_free_rate=risk_free_rate,
                volatility=call_volatility,
                option_type="CE",
            )

            call_forward_bs = (
                cls.forward_black_scholes_price(
                    forward_price=common_forward,
                    strike_price=strike_price,
                    time_to_expiry=time_to_expiry,
                    risk_free_rate=risk_free_rate,
                    volatility=call_volatility,
                    option_type="CE",
                )
            )

            (
                call_spot_difference,
                call_spot_difference_pct,
            ) = cls._premium_difference(
                market_premium=call_market,
                theoretical_premium=call_spot_bs,
            )

            (
                call_forward_difference,
                call_forward_difference_pct,
            ) = cls._premium_difference(
                market_premium=call_market,
                theoretical_premium=call_forward_bs,
            )

            results.append(
                ForwardPremiumAnalysis(
                    symbol=symbol,
                    expiry=expiry,
                    strike_price=option.strike_price,
                    option_type="CE",

                    spot_price=spot_price,
                    implied_forward=common_forward,

                    market_premium=call_market,

                    spot_bs_premium=call_spot_bs,
                    forward_bs_premium=call_forward_bs,

                    spot_difference=call_spot_difference,
                    spot_difference_pct=(
                        call_spot_difference_pct
                    ),

                    forward_difference=(
                        call_forward_difference
                    ),
                    forward_difference_pct=(
                        call_forward_difference_pct
                    ),

                    iv=call_iv,
                    time_to_expiry=time_to_expiry,

                    moneyness=cls.determine_moneyness(
                        spot_price=spot_price,
                        strike_price=option.strike_price,
                        option_type="CE",
                        atm_strike=atm_strike,
                    ),
                )
            )

            # =================================================
            # PUT
            # =================================================

            put_market = float(
                option.put_ltp
            )

            put_iv = max(
                float(option.put_iv),
                0.0,
            )

            put_volatility = (
                put_iv / 100.0
            )

            put_spot_bs = cls.black_scholes_price(
                spot_price=spot_price,
                strike_price=strike_price,
                time_to_expiry=time_to_expiry,
                risk_free_rate=risk_free_rate,
                volatility=put_volatility,
                option_type="PE",
            )

            put_forward_bs = (
                cls.forward_black_scholes_price(
                    forward_price=common_forward,
                    strike_price=strike_price,
                    time_to_expiry=time_to_expiry,
                    risk_free_rate=risk_free_rate,
                    volatility=put_volatility,
                    option_type="PE",
                )
            )

            (
                put_spot_difference,
                put_spot_difference_pct,
            ) = cls._premium_difference(
                market_premium=put_market,
                theoretical_premium=put_spot_bs,
            )

            (
                put_forward_difference,
                put_forward_difference_pct,
            ) = cls._premium_difference(
                market_premium=put_market,
                theoretical_premium=put_forward_bs,
            )

            results.append(
                ForwardPremiumAnalysis(
                    symbol=symbol,
                    expiry=expiry,
                    strike_price=option.strike_price,
                    option_type="PE",

                    spot_price=spot_price,
                    implied_forward=common_forward,

                    market_premium=put_market,

                    spot_bs_premium=put_spot_bs,
                    forward_bs_premium=put_forward_bs,

                    spot_difference=put_spot_difference,
                    spot_difference_pct=(
                        put_spot_difference_pct
                    ),

                    forward_difference=(
                        put_forward_difference
                    ),
                    forward_difference_pct=(
                        put_forward_difference_pct
                    ),

                    iv=put_iv,
                    time_to_expiry=time_to_expiry,

                    moneyness=cls.determine_moneyness(
                        spot_price=spot_price,
                        strike_price=option.strike_price,
                        option_type="PE",
                        atm_strike=atm_strike,
                    ),
                )
            )

        return results