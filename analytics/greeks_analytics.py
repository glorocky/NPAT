"""
analytics/greeks_analytics.py

Greeks analytics engine for NPAT.

Builds normalized Greeks analytics for ATM ±N option contracts
using the provider abstraction.

The analytics layer contains no Groww SDK-specific logic.
"""

from __future__ import annotations
from analytics.greeks_calculator import GreeksCalculator
from analytics.premium_analytics import PremiumAnalytics
from config import RISK_FREE_RATE
from providers.exceptions import ProviderDataError

from core.models import (
    GreeksAnalysis,
    GreeksSummary,
    OptionData,
    OptionGreeks,
)


class GreeksAnalytics:
    """
    Greeks analytics engine.

    Converts provider Greeks into normalized NPAT
    GreeksAnalysis models for dashboard and AI use.
    """

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
        Select ATM ±N strikes from the option chain.
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

        atm_index = min(
            range(len(sorted_options)),
            key=lambda index: abs(
                sorted_options[index].strike_price
                - atm_strike
            ),
        )

        start = max(
            0,
            atm_index - strikes_each_side,
        )

        end = min(
            len(sorted_options),
            atm_index + strikes_each_side + 1,
        )

        return sorted_options[start:end]
    
    # =====================================================
    # Greeks Summary
    # =====================================================

    @classmethod
    def summarize(
        cls,
        analysis: list[GreeksAnalysis],
        atm_strike: int,
    ) -> GreeksSummary:
        """
        Build an aggregated numerical summary from the
        ATM-window Greeks analysis.

        No directional BUY / SELL interpretation is
        performed here.
        """

        if not analysis:
            raise ValueError(
                "Greeks analysis cannot be empty."
            )

        if atm_strike <= 0:
            raise ValueError(
                "atm_strike must be greater than zero."
            )

        # -------------------------------------------------
        # Basic Context
        # -------------------------------------------------

        symbol = analysis[0].symbol
        expiry = analysis[0].expiry
        spot_price = float(
            analysis[0].spot_price
        )

        # -------------------------------------------------
        # ATM Contracts
        # -------------------------------------------------

        atm_contracts = [
            item
            for item in analysis
            if item.strike_price == atm_strike
        ]

        if len(atm_contracts) != 2:
            raise ValueError(
                "ATM CE and PE contracts are required."
            )

        try:
            atm_call = next(
                item
                for item in atm_contracts
                if item.option_type == "CE"
            )

            atm_put = next(
                item
                for item in atm_contracts
                if item.option_type == "PE"
            )

        except StopIteration as ex:
            raise ValueError(
                "ATM CE and PE contracts are required."
            ) from ex

        # -------------------------------------------------
        # Delta Balance
        # -------------------------------------------------
        #
        # Example:
        #
        # CE delta = +0.52
        # PE delta = -0.48
        #
        # delta_balance = +0.04
        #
        # Near zero = balanced ATM delta structure.
        # -------------------------------------------------

        delta_balance = (
            float(atm_call.delta)
            + float(atm_put.delta)
        )

        # -------------------------------------------------
        # IV Skew
        # -------------------------------------------------
        #
        # Positive:
        # PE IV > CE IV
        #
        # Negative:
        # CE IV > PE IV
        # -------------------------------------------------

        iv_skew = (
            float(atm_put.iv)
            - float(atm_call.iv)
        )

        # -------------------------------------------------
        # Gamma Concentration
        # -------------------------------------------------
        #
        # We want a STRIKE-level gamma measure rather than
        # simply selecting one CE or PE contract.
        # -------------------------------------------------

        gamma_by_strike: dict[int, float] = {}

        for item in analysis:

            gamma_by_strike.setdefault(
                item.strike_price,
                0.0,
            )

            gamma_by_strike[
                item.strike_price
            ] += abs(
                float(item.gamma)
            )

        highest_gamma_strike = max(
            gamma_by_strike,
            key=gamma_by_strike.get,
        )

        highest_gamma = gamma_by_strike[
            highest_gamma_strike
        ]

        # -------------------------------------------------
        # Theta
        # -------------------------------------------------

        total_call_theta = sum(
            float(item.theta)
            for item in analysis
            if item.option_type == "CE"
        )

        total_put_theta = sum(
            float(item.theta)
            for item in analysis
            if item.option_type == "PE"
        )

        total_theta = (
            total_call_theta
            + total_put_theta
        )

        # -------------------------------------------------
        # Vega
        # -------------------------------------------------

        total_call_vega = sum(
            float(item.vega)
            for item in analysis
            if item.option_type == "CE"
        )

        total_put_vega = sum(
            float(item.vega)
            for item in analysis
            if item.option_type == "PE"
        )

        total_vega = (
            total_call_vega
            + total_put_vega
        )

        # -------------------------------------------------
        # Summary
        # -------------------------------------------------

        return GreeksSummary(
            symbol=symbol,
            expiry=expiry,

            spot_price=spot_price,
            atm_strike=atm_strike,

            atm_call_delta=float(
                atm_call.delta
            ),

            atm_put_delta=float(
                atm_put.delta
            ),

            delta_balance=float(
                delta_balance
            ),

            atm_call_iv=float(
                atm_call.iv
            ),

            atm_put_iv=float(
                atm_put.iv
            ),

            iv_skew=float(
                iv_skew
            ),

            highest_gamma_strike=int(
                highest_gamma_strike
            ),

            highest_gamma=float(
                highest_gamma
            ),

            total_call_theta=float(
                total_call_theta
            ),

            total_put_theta=float(
                total_put_theta
            ),

            total_theta=float(
                total_theta
            ),

            total_call_vega=float(
                total_call_vega
            ),

            total_put_vega=float(
                total_put_vega
            ),

            total_vega=float(
                total_vega
            ),
        )

    # =====================================================
    # Moneyness
    # =====================================================

    @staticmethod
    def determine_moneyness(
        strike_price: int,
        atm_strike: int,
        option_type: str,
    ) -> str:
        """
        Determine ITM / ATM / OTM relative to ATM strike.
        """

        option_type = option_type.upper()

        if option_type not in {
            "CE",
            "PE",
        }:
            raise ValueError(
                "option_type must be CE or PE."
            )

        if strike_price == atm_strike:
            return "ATM"

        if option_type == "CE":

            if strike_price < atm_strike:
                return "ITM"

            return "OTM"

        if strike_price > atm_strike:
            return "ITM"

        return "OTM"
    
    # =====================================================
    # Provider Greeks With Calculated Fallback
    # =====================================================

    @staticmethod
    def _get_greeks_with_fallback(
        provider,
        exchange: str,
        symbol: str,
        expiry: str,
        strike_price: int,
        option_type: str,
        market_price: float,
        spot_price: float,
        provider_iv: float = 0.0,
    ):
        """
        Return provider Greeks when available.

        If the provider specifically returns missing or
        incomplete Greeks data, derive IV and Greeks from
        the observed option market premium.

        Other provider failures are re-raised unchanged.
        """

        try:
            return provider.get_greeks(
                exchange=exchange,
                symbol=symbol,
                expiry=expiry,
                strike=strike_price,
                option_type=option_type,
            )

        except ProviderDataError as ex:

            message = str(ex).lower()

            greeks_unavailable = (
                "greeks" in message
                and (
                    "incomplete" in message
                    or "missing" in message
                )
            )

            if not greeks_unavailable:
                raise

            # -------------------------------------------------
            # Validate Fallback Inputs
            # -------------------------------------------------
            market_price = float(
                market_price
            )

            spot_price = float(
                spot_price
            )

            provider_iv = float(
                provider_iv or 0.0
            )

            if spot_price <= 0:
                raise ProviderDataError(
                    "Cannot calculate fallback Greeks because "
                    "spot price is unavailable."
                ) from ex

            if (
                provider_iv <= 0.0
                and market_price <= 0.0
            ):
                raise ProviderDataError(
                    "Cannot calculate fallback Greeks because "
                    "both provider IV and option market price "
                    "are unavailable."
                ) from ex

            # -------------------------------------------------
            # Time To Expiry
            # -------------------------------------------------

            time_to_expiry = (
                PremiumAnalytics.calculate_time_to_expiry(
                    expiry=expiry,
                )
            )

            if time_to_expiry <= 0:
                raise ProviderDataError(
                    "Cannot calculate fallback Greeks because "
                    "the option has expired."
                ) from ex

            # -------------------------------------------------
            # Calculate Market-Implied Greeks
            # -------------------------------------------------

            try:

                # -------------------------------------------------
                # Prefer Provider IV
                # -------------------------------------------------

                if provider_iv > 0.0:

                    values = GreeksCalculator.calculate_greeks(
                        spot_price=spot_price,
                        strike_price=float(strike_price),
                        time_to_expiry=time_to_expiry,
                        risk_free_rate=RISK_FREE_RATE,
                        volatility=provider_iv / 100.0,
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
                        iv=provider_iv,
                    )

                # -------------------------------------------------
                # Last Resort: Derive IV From LTP
                # -------------------------------------------------

                return GreeksCalculator.build_option_greeks(
                    symbol=symbol,
                    expiry=expiry,
                    strike_price=strike_price,
                    option_type=option_type,
                    market_price=market_price,
                    spot_price=spot_price,
                    time_to_expiry=time_to_expiry,
                    risk_free_rate=RISK_FREE_RATE,
                )

            except (TypeError, ValueError) as calc_ex:
                raise ProviderDataError(
                    "Unable to calculate fallback Greeks from "
                    "the available option market data."
                ) from calc_ex

    # =====================================================
    # Build Greeks
    # =====================================================

    @classmethod
    def analyze_atm_window(
        cls,
        provider,
        symbol: str,
        exchange: str,
        expiry: str,
        options: list[OptionData],
        atm_strike: int,
        strikes_each_side: int = 3,
    ) -> list[GreeksAnalysis]:
        """
        Fetch and normalize Greeks for ATM ±N strikes.

        Produces one GreeksAnalysis for CE and one for PE
        at each selected strike.
        """

        if provider is None:
            raise ValueError(
                "provider is required."
            )

        if not symbol:
            raise ValueError(
                "symbol is required."
            )

        if not exchange:
            raise ValueError(
                "exchange is required."
            )

        if not expiry:
            raise ValueError(
                "expiry is required."
            )

        selected_options = cls.select_atm_window(
            options=options,
            atm_strike=atm_strike,
            strikes_each_side=strikes_each_side,
        )

        results: list[GreeksAnalysis] = []

        for option in selected_options:

            # =================================================
            # CALL
            # =================================================

            call_greeks = cls._get_greeks_with_fallback(
                provider=provider,
                exchange=exchange,
                symbol=symbol,
                expiry=expiry,
                strike_price=option.strike_price,
                option_type="CE",
                market_price=option.call_ltp,
                spot_price=option.underlying_price,
                provider_iv=option.call_iv,
            )

            results.append(
                GreeksAnalysis(
                    symbol=symbol,
                    expiry=expiry,

                    strike_price=option.strike_price,
                    option_type="CE",

                    spot_price=float(
                        option.underlying_price
                    ),

                    option_ltp=float(
                        option.call_ltp
                    ),

                    delta=float(
                        call_greeks.delta
                    ),

                    gamma=float(
                        call_greeks.gamma
                    ),

                    theta=float(
                        call_greeks.theta
                    ),

                    vega=float(
                        call_greeks.vega
                    ),

                    rho=float(
                        call_greeks.rho
                    ),

                    iv=float(
                        call_greeks.iv
                    ),

                    moneyness=cls.determine_moneyness(
                        strike_price=option.strike_price,
                        atm_strike=atm_strike,
                        option_type="CE",
                    ),
                )
            )

            # =================================================
            # PUT
            # =================================================

            put_greeks = cls._get_greeks_with_fallback(
                provider=provider,
                exchange=exchange,
                symbol=symbol,
                expiry=expiry,
                strike_price=option.strike_price,
                option_type="PE",
                market_price=option.put_ltp,
                spot_price=option.underlying_price,
                provider_iv=option.put_iv,
            )

            results.append(
                GreeksAnalysis(
                    symbol=symbol,
                    expiry=expiry,

                    strike_price=option.strike_price,
                    option_type="PE",

                    spot_price=float(
                        option.underlying_price
                    ),

                    option_ltp=float(
                        option.put_ltp
                    ),

                    delta=float(
                        put_greeks.delta
                    ),

                    gamma=float(
                        put_greeks.gamma
                    ),

                    theta=float(
                        put_greeks.theta
                    ),

                    vega=float(
                        put_greeks.vega
                    ),

                    rho=float(
                        put_greeks.rho
                    ),

                    iv=float(
                        put_greeks.iv
                    ),

                    moneyness=cls.determine_moneyness(
                        strike_price=option.strike_price,
                        atm_strike=atm_strike,
                        option_type="PE",
                    ),
                )
            )

        return results