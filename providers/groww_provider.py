"""
=========================================================
NPAT - Groww Provider

Production implementation...
=========================================================

Purpose
-------
Production implementation of the Groww market data provider.

This class acts as an adapter between the Groww SDK and
the NPAT provider interface.

Responsibilities
----------------
- Live Quotes
- Historical Data
- Option Chain
- Expiry Dates
- Greeks
- Market Snapshot

Author  : Rocky Chopra
Version : 2.0.0
=========================================================
"""

from __future__ import annotations

from datetime import datetime

# =====================================================
# Third-Party Imports
# =====================================================

from growwapi.groww.client import GrowwAPI

# =====================================================
# NPAT Core Imports
# =====================================================

from core.models import (
    FutureData,
    HistoricalCandle,
    MarketSnapshot,
    OptionData,
    OptionGreeks,
    Quote,
)

# =====================================================
# NPAT Provider Imports
# =====================================================

from providers.base_provider import BaseProvider
from providers.exceptions import (
    ProviderAuthenticationError,
    ProviderConnectionError,
    ProviderDataError,
)


class GrowwProvider(BaseProvider):
    """
    Groww implementation of BaseProvider.

    This class converts Groww SDK responses into NPAT
    core model objects.
    """

    def __init__(self, access_token: str):
        """
        Initialize Groww Provider.

        Parameters
        ----------
        access_token : str
            Groww API access token.
        """

        super().__init__("Groww")

        if not access_token:
            raise ProviderAuthenticationError(
                "Groww access token is missing."
            )

        try:
            
            self._api: GrowwAPI = GrowwAPI(access_token)

            self.logger.info(
                "Groww Provider initialized successfully."
            )

        except Exception as ex:
            raise ProviderAuthenticationError(
                f"Unable to initialize Groww Provider: {ex}"
            ) from ex
    
     # =====================================================
    # API Client
    # =====================================================
    @property
    def api_client(self) -> GrowwAPI:
        """
        Return the underlying Groww SDK client.
        """

        return self._api

    # =====================================================
    # Live Quote
    # =====================================================

    def get_quote(
        self,
        trading_symbol: str,
        exchange: str,
        segment: str,
    ) -> Quote:
        """
        Return the latest market quote for a trading symbol.

        The Groww SDK response is normalized into the
        NPAT Quote model.
        """

        response = self._execute(
            "get_quote",
            self.api_client.get_quote,
            trading_symbol=trading_symbol,
            exchange=exchange,
            segment=segment,
        )

        if not isinstance(response, dict):
            raise ProviderDataError(
                "Groww get_quote returned an invalid response."
            )

        ohlc = response.get("ohlc")

        if not isinstance(ohlc, dict):
            raise ProviderDataError(
                "Groww get_quote response is missing OHLC data."
            )

        required_fields = (
            "last_price",
        )

        missing_fields = [
            field
            for field in required_fields
            if response.get(field) is None
        ]

        required_ohlc_fields = (
            "open",
            "high",
            "low",
            "close",
        )

        missing_ohlc_fields = [
            field
            for field in required_ohlc_fields
            if ohlc.get(field) is None
        ]

        if missing_fields or missing_ohlc_fields:
            raise ProviderDataError(
                "Groww get_quote response contains incomplete "
                "market data."
            )

        try:
            return Quote(
                symbol=trading_symbol,
                exchange=exchange,
                last_price=float(response["last_price"]),
                open=float(ohlc["open"]),
                high=float(ohlc["high"]),
                low=float(ohlc["low"]),
                previous_close=float(ohlc["close"]),
                volume=int(response.get("volume") or 0),
                timestamp=None,
            )

        except (TypeError, ValueError, KeyError) as ex:
            raise ProviderDataError(
                "Unable to convert Groww quote response "
                "into NPAT Quote model."
            ) from ex
            
    # =====================================================
    # Futures Contract
    # =====================================================

    def get_future(
        self,
        symbol: str,
        exchange: str = "NSE",
        expiry: str | None = None,
    ) -> FutureData:
        """
        Return normalized futures data for an underlying.

        If expiry is not supplied, the nearest non-expired
        futures contract is selected automatically.
        """

        if not symbol:
            raise ValueError(
                "symbol is required."
            )

        if not exchange:
            raise ValueError(
                "exchange is required."
            )

        symbol = symbol.upper()
        exchange = exchange.upper()

        # -------------------------------------------------
        # Instrument Master
        # -------------------------------------------------

        instruments = self._execute(
            "get_all_instruments",
            self.api_client.get_all_instruments,
        )

        if instruments is None or instruments.empty:
            raise ProviderDataError(
                "Groww instrument master is empty."
            )

        required_columns = {
            "exchange",
            "trading_symbol",
            "instrument_type",
            "segment",
            "underlying_symbol",
            "expiry_date",
            "lot_size",
            "exchange_token",
        }

        missing_columns = (
            required_columns
            - set(instruments.columns)
        )

        if missing_columns:
            raise ProviderDataError(
                "Groww instrument master is missing required "
                f"columns: {sorted(missing_columns)}"
            )

        # -------------------------------------------------
        # Futures Contracts
        # -------------------------------------------------

        contracts = instruments[
            (instruments["exchange"] == exchange)
            & (instruments["segment"] == "FNO")
            & (instruments["instrument_type"] == "FUT")
            & (instruments["underlying_symbol"] == symbol)
        ].copy()

        if contracts.empty:
            raise ProviderDataError(
                f"No futures contracts found for {symbol}."
            )

        # -------------------------------------------------
        # Normalize Expiry
        # -------------------------------------------------

        try:
            contracts["expiry_date"] = contracts[
                "expiry_date"
            ].astype(str)

        except Exception as ex:
            raise ProviderDataError(
                "Unable to normalize futures expiry dates."
            ) from ex

        # -------------------------------------------------
        # Select Contract
        # -------------------------------------------------

        if expiry:

            matching = contracts[
                contracts["expiry_date"] == expiry
            ]

            if matching.empty:
                raise ProviderDataError(
                    f"No {symbol} futures contract found "
                    f"for expiry {expiry}."
                )

            contract = matching.iloc[0]

        else:

            today = datetime.now().date()

            active_contracts = contracts[
                contracts["expiry_date"].apply(
                    lambda value: (
                        datetime.strptime(
                            value,
                            "%Y-%m-%d",
                        ).date()
                        >= today
                    )
                )
            ]

            if active_contracts.empty:
                raise ProviderDataError(
                    f"No active futures contracts found "
                    f"for {symbol}."
                )

            active_contracts = (
                active_contracts.sort_values(
                    "expiry_date"
                )
            )

            contract = active_contracts.iloc[0]

        trading_symbol = str(
            contract["trading_symbol"]
        )

        contract_expiry = str(
            contract["expiry_date"]
        )

        # -------------------------------------------------
        # Live Futures Quote
        # -------------------------------------------------

        response = self._execute(
            "get_future_quote",
            self.api_client.get_quote,
            trading_symbol=trading_symbol,
            exchange=exchange,
            segment="FNO",
        )

        if not isinstance(response, dict):
            raise ProviderDataError(
                "Groww futures quote returned an invalid "
                "response."
            )

        ohlc = response.get("ohlc")

        if not isinstance(ohlc, dict):
            raise ProviderDataError(
                "Groww futures quote is missing OHLC data."
            )

        required_quote_fields = (
            "last_price",
            "open_interest",
        )

        missing_quote_fields = [
            field
            for field in required_quote_fields
            if response.get(field) is None
        ]

        required_ohlc_fields = (
            "open",
            "high",
            "low",
            "close",
        )

        missing_ohlc_fields = [
            field
            for field in required_ohlc_fields
            if ohlc.get(field) is None
        ]

        if (
            missing_quote_fields
            or missing_ohlc_fields
        ):
            raise ProviderDataError(
                "Groww futures quote contains incomplete "
                "market data."
            )

        # -------------------------------------------------
        # Normalize
        # -------------------------------------------------

        try:

            return FutureData(
                symbol=symbol,
                exchange=exchange,
                trading_symbol=trading_symbol,
                expiry=contract_expiry,

                lot_size=int(
                    contract["lot_size"] or 0
                ),

                exchange_token=str(
                    contract["exchange_token"]
                ),

                last_price=float(
                    response["last_price"]
                ),

                open=float(
                    ohlc["open"]
                ),

                high=float(
                    ohlc["high"]
                ),

                low=float(
                    ohlc["low"]
                ),

                previous_close=float(
                    ohlc["close"]
                ),

                open_interest=int(
                    response.get(
                        "open_interest"
                    ) or 0
                ),

                previous_open_interest=int(
                    response.get(
                        "previous_open_interest"
                    ) or 0
                ),

                oi_change=int(
                    response.get(
                        "oi_day_change"
                    ) or 0
                ),

                oi_change_pct=float(
                    response.get(
                        "oi_day_change_percentage"
                    ) or 0.0
                ),

                volume=int(
                    response.get(
                        "volume"
                    ) or 0
                ),

                last_trade_quantity=int(
                    response.get(
                        "last_trade_quantity"
                    ) or 0
                ),

                total_buy_quantity=int(
                    response.get(
                        "total_buy_quantity"
                    ) or 0
                ),

                total_sell_quantity=int(
                    response.get(
                        "total_sell_quantity"
                    ) or 0
                ),

                timestamp=None,
            )

        except (
            TypeError,
            ValueError,
            KeyError,
        ) as ex:

            raise ProviderDataError(
                "Unable to convert Groww futures data "
                "into NPAT FutureData model."
            ) from ex
            
    # =====================================================
    # Batch LTP
    # =====================================================

    def get_ltp_batch(
        self,
        symbols: list[str],
        exchange: str = "NSE",
        segment: str = "CASH",
    ) -> dict[str, float]:
        """
        Return latest prices for multiple symbols.

        Groww expects exchange-qualified symbols such as
        NSE_RELIANCE. The response is normalized back to
        plain NPAT symbols such as RELIANCE.
        """

        if not symbols:
            return {}

        normalized_symbols = [
            str(symbol).strip().upper()
            for symbol in symbols
            if str(symbol).strip()
        ]

        exchange_symbols = tuple(
            f"{exchange.upper()}_{symbol}"
            for symbol in normalized_symbols
        )

        response = self._execute(
            "get_ltp_batch",
            self.api_client.get_ltp,
            exchange_trading_symbols=exchange_symbols,
            segment=segment,
        )

        if not isinstance(response, dict):
            raise ProviderDataError(
                "Groww get_ltp returned an invalid response."
            )

        result: dict[str, float] = {}

        prefix = f"{exchange.upper()}_"

        for key, value in response.items():

            symbol = str(key)

            if symbol.startswith(prefix):
                symbol = symbol[len(prefix):]

            try:
                result[symbol] = float(value)

            except (TypeError, ValueError):
                raise ProviderDataError(
                    f"Invalid LTP returned for {symbol}."
                )

        return result

    # =====================================================
    # Batch OHLC
    # =====================================================

    def get_ohlc_batch(
        self,
        symbols: list[str],
        exchange: str = "NSE",
        segment: str = "CASH",
    ) -> dict[str, dict[str, float]]:
        """
        Return OHLC data for multiple symbols.

        Groww response keys are normalized from
        NSE_RELIANCE to RELIANCE.
        """

        if not symbols:
            return {}

        normalized_symbols = [
            str(symbol).strip().upper()
            for symbol in symbols
            if str(symbol).strip()
        ]

        exchange_symbols = tuple(
            f"{exchange.upper()}_{symbol}"
            for symbol in normalized_symbols
        )

        response = self._execute(
            "get_ohlc_batch",
            self.api_client.get_ohlc,
            exchange_trading_symbols=exchange_symbols,
            segment=segment,
        )

        if not isinstance(response, dict):
            raise ProviderDataError(
                "Groww get_ohlc returned an invalid response."
            )

        result: dict[str, dict[str, float]] = {}

        prefix = f"{exchange.upper()}_"

        for key, data in response.items():

            if not isinstance(data, dict):
                raise ProviderDataError(
                    f"Invalid OHLC returned for {key}."
                )

            symbol = str(key)

            if symbol.startswith(prefix):
                symbol = symbol[len(prefix):]

            required = (
                "open",
                "high",
                "low",
                "close",
            )

            missing = [
                field
                for field in required
                if data.get(field) is None
            ]

            if missing:
                raise ProviderDataError(
                    f"OHLC data for {symbol} is missing "
                    f"fields: {missing}"
                )

            try:
                result[symbol] = {
                    "open": float(data["open"]),
                    "high": float(data["high"]),
                    "low": float(data["low"]),
                    "previous_close": float(data["close"]),
                }

            except (TypeError, ValueError, KeyError) as ex:
                raise ProviderDataError(
                    f"Unable to normalize OHLC data "
                    f"for {symbol}."
                ) from ex

        return result

    # =====================================================
    # Historical Data
    # =====================================================

    def get_historical_data(
        self,
        exchange: str,
        segment: str,
        groww_symbol: str,
        start_time: str,
        end_time: str,
        candle_interval: str,
    ) -> list[HistoricalCandle]:
        """
        Return historical OHLCV candles.

        The Groww SDK response is normalized into
        NPAT HistoricalCandle models.
        """

        response = self._execute(
            "get_historical_data",
            self.api_client.get_historical_candles,
            exchange=exchange,
            segment=segment,
            groww_symbol=groww_symbol,
            start_time=start_time,
            end_time=end_time,
            candle_interval=candle_interval,
        )

        if not isinstance(response, dict):
            raise ProviderDataError(
                "Groww historical data returned an invalid response."
            )

        candles = response.get("candles")

        if not isinstance(candles, list):
            raise ProviderDataError(
                "Groww historical response is missing candle data."
            )

        result: list[HistoricalCandle] = []

        for candle in candles:

            if not isinstance(candle, (list, tuple)) or len(candle) < 6:
                raise ProviderDataError(
                    "Groww returned an invalid historical candle."
                )

            try:
                timestamp = datetime.fromisoformat(candle[0])

                result.append(
                    HistoricalCandle(
                        timestamp=timestamp,
                        open=float(candle[1]),
                        high=float(candle[2]),
                        low=float(candle[3]),
                        close=float(candle[4]),
                        volume=int(candle[5] or 0),
                    )
                )

            except (TypeError, ValueError) as ex:
                raise ProviderDataError(
                    "Unable to convert Groww historical candle "
                    "into NPAT HistoricalCandle model."
                ) from ex

        return result

    # =====================================================
    # Expiry Dates
    # =====================================================

    def get_expiries(
        self,
        exchange: str,
        underlying_symbol: str,
        year: int | None = None,
        month: int | None = None,
    ) -> list[str]:
        """
        Return available option expiry dates.

        The Groww SDK response is normalized into
        a list of expiry-date strings.
        """

        response = self._execute(
            "get_expiries",
            self.api_client.get_expiries,
            exchange=exchange,
            underlying_symbol=underlying_symbol,
            year=year,
            month=month,
        )

        if not isinstance(response, dict):
            raise ProviderDataError(
                "Groww get_expiries returned an invalid response."
            )

        expiries = response.get("expiries")

        if not isinstance(expiries, list):
            raise ProviderDataError(
                "Groww get_expiries response is missing expiry data."
            )

        if not all(
            isinstance(expiry, str) and expiry
            for expiry in expiries
        ):
            raise ProviderDataError(
                "Groww get_expiries returned invalid expiry values."
            )

        return expiries


    # =====================================================
    # Option Chain
    # =====================================================
    def get_option_chain(
        self,
        exchange: str,
        symbol: str,
        expiry: str | None = None,
    ) -> list[OptionData]:
        """
        Return the option chain for an underlying and expiry.

        The Groww SDK response is normalized into
        NPAT OptionData models.
        """
        if not expiry:
            raise ValueError(
                "Expiry is required for Groww option chain."
            )

        response = self._execute(
            "get_option_chain",
            self.api_client.get_option_chain,
            exchange=exchange,
            underlying=symbol,
            expiry_date=expiry,
        )
        
        # =================================================
        # Validate Response
        # =================================================

        if not isinstance(response, dict):
            raise ProviderDataError(
                "Groww get_option_chain returned an invalid response."
            )

        # =================================================
        # Underlying LTP
        # =================================================

        underlying_ltp = response.get("underlying_ltp")

        if underlying_ltp is None:
            raise ProviderDataError(
                "Groww option chain is missing underlying LTP."
            )

        # =================================================
        # Strike Data
        # =================================================

        strikes = response.get("strikes")

        if not isinstance(strikes, dict):
            raise ProviderDataError(
                "Groww option chain is missing strike data."
            )

        if not strikes:
            raise ProviderDataError(
                "Groww option chain contains no strikes."
            )

        # =================================================
        # Normalize Option Chain
        # =================================================

        result: list[OptionData] = []

        for strike_key, strike_data in strikes.items():

            if not isinstance(strike_data, dict):
                continue

            try:
                strike_price = int(float(strike_key))
            except (TypeError, ValueError):
                continue

            # =============================================
            # CE / PE Data
            # =============================================

            call_data = strike_data.get("CE") or {}
            put_data = strike_data.get("PE") or {}

            if not isinstance(call_data, dict):
                call_data = {}

            if not isinstance(put_data, dict):
                put_data = {}

            # =============================================
            # Greeks
            # =============================================

            call_greeks = call_data.get("greeks") or {}
            put_greeks = put_data.get("greeks") or {}

            if not isinstance(call_greeks, dict):
                call_greeks = {}

            if not isinstance(put_greeks, dict):
                put_greeks = {}

            # =============================================
            # Create NPAT OptionData
            # =============================================

            try:
                option = OptionData(
                    strike_price=strike_price,
                    expiry=expiry,
                    underlying_price=float(underlying_ltp),

                    # CALL
                    call_oi=int(
                        call_data.get("open_interest") or 0
                    ),
                    call_change_oi=0,
                    call_volume=int(
                        call_data.get("volume") or 0
                    ),
                    call_iv=float(
                        call_greeks.get("iv") or 0.0
                    ),
                    call_ltp=float(
                        call_data.get("ltp") or 0.0
                    ),

                    # PUT
                    put_oi=int(
                        put_data.get("open_interest") or 0
                    ),
                    put_change_oi=0,
                    put_volume=int(
                        put_data.get("volume") or 0
                    ),
                    put_iv=float(
                        put_greeks.get("iv") or 0.0
                    ),
                    put_ltp=float(
                        put_data.get("ltp") or 0.0
                    ),
                )

            except (TypeError, ValueError) as ex:
                raise ProviderDataError(
                    f"Unable to normalize Groww option data "
                    f"for strike {strike_key}."
                ) from ex

            result.append(option)

        # =================================================
        # Validate Normalized Result
        # =================================================

        if not result:
            raise ProviderDataError(
                "Groww option chain contains no valid strikes."
            )

        # =================================================
        # Sort by Strike Price
        # =================================================

        result.sort(
            key=lambda option: option.strike_price
        )

        return result
    
    # =====================================================
    # Option Greeks
    # =====================================================

    def get_greeks(
        self,
        exchange: str,
        symbol: str,
        expiry: str,
        strike: int,
        option_type: str,
    ) -> OptionGreeks:
        """
        Return normalized option Greeks.

        NPAT provides the underlying symbol, expiry,
        strike and option type.

        GrowwProvider converts those values into the
        Groww trading-symbol format internally.
        """

        # =================================================
        # Validate Inputs
        # =================================================

        option_type = option_type.upper()

        if option_type not in {"CE", "PE"}:
            raise ValueError(
                "option_type must be CE or PE."
            )

        if strike <= 0:
            raise ValueError(
                "strike must be greater than zero."
            )

        try:
            expiry_date = datetime.strptime(
                expiry,
                "%Y-%m-%d",
            )
        except ValueError as ex:
            raise ValueError(
                "expiry must use YYYY-MM-DD format."
            ) from ex

        # =================================================
        # Resolve Groww Option Contract
        # =================================================

        instruments = self._execute(
            "get_all_instruments",
            self.api_client.get_all_instruments,
        )

        if instruments is None or instruments.empty:
            raise ProviderDataError(
                "Groww instrument master is empty."
            )

        required_columns = {
            "exchange",
            "trading_symbol",
            "instrument_type",
            "segment",
            "underlying_symbol",
            "expiry_date",
            "strike_price",
        }

        missing_columns = (
            required_columns
            - set(instruments.columns)
        )

        if missing_columns:
            raise ProviderDataError(
                "Groww instrument master is missing required "
                f"columns: {sorted(missing_columns)}"
            )

        contracts = instruments[
            (instruments["exchange"] == exchange.upper())
            & (instruments["segment"] == "FNO")
            & (
                instruments["underlying_symbol"]
                == symbol.upper()
            )
        ].copy()

        if contracts.empty:
            raise ProviderDataError(
                f"No option contracts found for {symbol}."
            )

        contracts["expiry_date"] = (
            contracts["expiry_date"].astype(str)
        )

        contracts["strike_price"] = (
            contracts["strike_price"]
        ).astype(float)

        contracts = contracts[
            (contracts["expiry_date"] == expiry)
            & (
                contracts["strike_price"]
                == float(strike)
            )
            & (
                contracts["trading_symbol"]
                .astype(str)
                .str.endswith(option_type)
            )
        ]

        if contracts.empty:
            raise ProviderDataError(
                f"No {symbol} {option_type} option contract "
                f"found for strike {strike} and expiry "
                f"{expiry}."
            )

        contract = contracts.iloc[0]

        trading_symbol = str(
            contract["trading_symbol"]
        )
        # =================================================
        # Execute Groww API
        # =================================================

        response = self._execute(
            "get_greeks",
            self.api_client.get_greeks,
            exchange=exchange,
            underlying=symbol,
            trading_symbol=trading_symbol,
            expiry=expiry,
        )
        
        
        # =================================================
        # Validate Response
        # =================================================

        if not isinstance(response, dict):
            raise ProviderDataError(
                "Groww get_greeks returned an invalid response."
            )

        greeks = response.get("greeks")

        if not isinstance(greeks, dict):
            raise ProviderDataError(
                "Groww get_greeks response is missing Greeks data."
            )

        # =================================================
        # Validate Greeks
        # =================================================

        required_fields = (
            "delta",
            "gamma",
            "theta",
            "vega",
            "rho",
            "iv",
        )

        missing_fields = [
            field
            for field in required_fields
            if greeks.get(field) is None
        ]

        if missing_fields:
            raise ProviderDataError(
                "Groww get_greeks response contains incomplete "
                f"Greeks data: {', '.join(missing_fields)}."
            )

        # =================================================
        # Normalize
        # =================================================

        try:
            return OptionGreeks(
                symbol=symbol,
                expiry=expiry,
                strike_price=int(strike),
                option_type=option_type,
                delta=float(greeks["delta"]),
                gamma=float(greeks["gamma"]),
                theta=float(greeks["theta"]),
                vega=float(greeks["vega"]),
                rho=float(greeks["rho"]),
                iv=float(greeks["iv"]),
            )

        except (TypeError, ValueError, KeyError) as ex:
            raise ProviderDataError(
                "Unable to convert Groww Greeks response "
                "into NPAT OptionGreeks model."
            ) from ex
    # =====================================================
    # Health Check
    # =====================================================

    def health_check(self) -> bool:
        """
        Verify the Groww SDK is initialized.
        """

        return self.api_client is not None

