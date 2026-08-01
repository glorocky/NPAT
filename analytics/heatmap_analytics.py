"""
=========================================================
NPAT - Heatmap Analytics

Calculates heatmap metrics for index constituents.

This module contains analytics only. It does not fetch
market data and does not depend on a specific provider.
=========================================================
"""

from __future__ import annotations

from core.models import (
    HeatmapStock,
    HeatmapSummary,
    SectorBreadth,
)


class HeatmapAnalytics:
    """
    Calculate heatmap analytics for index constituents.
    """

    # =====================================================
    # Percentage Change
    # =====================================================

    @staticmethod
    def _change_pct(
        current: float,
        previous: float,
    ) -> float:
        """
        Calculate percentage change.

        Returns 0.0 when previous value is zero.
        """

        if previous == 0:
            return 0.0

        return (
            (current - previous)
            / previous
        ) * 100.0

    # =====================================================
    # Direction
    # =====================================================

    @staticmethod
    def _direction(change: float) -> str:
        """
        Classify price direction.
        """

        if change > 0:
            return "GAINER"

        if change < 0:
            return "LOSER"

        return "FLAT"

    # =====================================================
    # Analyze One Stock
    # =====================================================

    @classmethod
    def analyze_stock(
        cls,
        symbol: str,
        company_name: str,
        sector: str,
        exchange: str,
        last_price: float,
        previous_close: float,
        open_price: float,
        high: float,
        low: float,
    ) -> HeatmapStock:
        """
        Analyze one constituent for the heatmap.
        """

        # -------------------------------------------------
        # Validation
        # -------------------------------------------------

        if not symbol:
            raise ValueError(
                "symbol is required."
            )

        if not company_name:
            raise ValueError(
                "company_name is required."
            )

        if not sector:
            raise ValueError(
                "sector is required."
            )

        if not exchange:
            raise ValueError(
                "exchange is required."
            )

        if last_price < 0:
            raise ValueError(
                "last_price cannot be negative."
            )

        if previous_close < 0:
            raise ValueError(
                "previous_close cannot be negative."
            )

        if open_price < 0:
            raise ValueError(
                "open_price cannot be negative."
            )

        if high < 0:
            raise ValueError(
                "high cannot be negative."
            )

        if low < 0:
            raise ValueError(
                "low cannot be negative."
            )

        # -------------------------------------------------
        # Price Change
        # -------------------------------------------------

        change = (
            last_price
            - previous_close
        )

        change_pct = cls._change_pct(
            current=last_price,
            previous=previous_close,
        )

        direction = cls._direction(
            change=change,
        )

        # -------------------------------------------------
        # Result
        # -------------------------------------------------

        return HeatmapStock(
            symbol=symbol.strip().upper(),
            company_name=company_name.strip(),
            sector=sector.strip(),
            exchange=exchange.strip().upper(),

            last_price=float(last_price),
            previous_close=float(previous_close),

            change=float(change),
            change_pct=float(change_pct),

            open=float(open_price),
            high=float(high),
            low=float(low),

            direction=direction,
        )
        
    # =====================================================
    # Analyze Constituents
    # =====================================================

    @classmethod
    def analyze_constituents(
        cls,
        constituents,
        ltp: dict[str, float],
        ohlc: dict[str, dict[str, float]],
    ) -> list[HeatmapStock]:
        """
        Analyze multiple index constituents.

        constituents must provide:
        symbol
        company_name
        sector
        exchange
        """

        results: list[HeatmapStock] = []

        for row in constituents.itertuples(
            index=False
        ):

            symbol = str(
                row.symbol
            ).strip().upper()

            # ---------------------------------------------
            # Validate Market Data Coverage
            # ---------------------------------------------

            if symbol not in ltp:
                raise ValueError(
                    f"LTP data missing for {symbol}."
                )

            if symbol not in ohlc:
                raise ValueError(
                    f"OHLC data missing for {symbol}."
                )

            stock_ohlc = ohlc[symbol]

            required_ohlc = (
                "open",
                "high",
                "low",
                "previous_close",
            )

            missing = [
                field
                for field in required_ohlc
                if stock_ohlc.get(field) is None
            ]

            if missing:
                raise ValueError(
                    f"OHLC data for {symbol} is missing "
                    f"fields: {missing}"
                )

            # ---------------------------------------------
            # Analyze Stock
            # ---------------------------------------------

            analysis = cls.analyze_stock(
                symbol=symbol,
                company_name=row.company_name,
                sector=row.sector,
                exchange=row.exchange,

                last_price=ltp[symbol],

                previous_close=(
                    stock_ohlc["previous_close"]
                ),

                open_price=stock_ohlc["open"],
                high=stock_ohlc["high"],
                low=stock_ohlc["low"],
            )

            results.append(
                analysis
            )

        return results
    
    # =====================================================
    # Heatmap Summary
    # =====================================================

    @classmethod
    def summarize(
        cls,
        heatmap: list[HeatmapStock],
    ) -> HeatmapSummary:
        """
        Build aggregate market breadth statistics from
        constituent heatmap analytics.
        """

        if not heatmap:
            raise ValueError(
                "heatmap cannot be empty."
            )
            
        # -------------------------------------------------
        # Breadth Counts
        # -------------------------------------------------

        gainers = sum(
            stock.direction == "GAINER"
            for stock in heatmap
        )

        losers = sum(
            stock.direction == "LOSER"
            for stock in heatmap
        )

        flat = sum(
            stock.direction == "FLAT"
            for stock in heatmap
        )

        total_stocks = len(heatmap)

        # -------------------------------------------------
        # Advance / Decline Ratio
        # -------------------------------------------------

        if losers == 0:
            advance_decline_ratio = float(gainers)
        else:
            advance_decline_ratio = (
                gainers / losers
            )

        # -------------------------------------------------
        # Average Change
        # -------------------------------------------------

        average_change_pct = (
            sum(
                stock.change_pct
                for stock in heatmap
            )
            / total_stocks
        )

        # -------------------------------------------------
        # Strongest / Weakest
        # -------------------------------------------------

        strongest = max(
            heatmap,
            key=lambda stock: stock.change_pct,
        )

        weakest = min(
            heatmap,
            key=lambda stock: stock.change_pct,
        )

        # -------------------------------------------------
        # Result
        # -------------------------------------------------

        return HeatmapSummary(
            total_stocks=total_stocks,

            gainers=gainers,
            losers=losers,
            flat=flat,

            advance_decline_ratio=float(
                advance_decline_ratio
            ),

            average_change_pct=float(
                average_change_pct
            ),

            strongest_symbol=strongest.symbol,
            strongest_change_pct=float(
                strongest.change_pct
            ),

            weakest_symbol=weakest.symbol,
            weakest_change_pct=float(
                weakest.change_pct
            ),
        )
            
    # =====================================================
    # Sector Breadth
    # =====================================================

    @classmethod
    def summarize_sectors(
        cls,
        heatmap: list[HeatmapStock],
    ) -> list[SectorBreadth]:
        """
        Build breadth analytics for each sector represented
        in the heatmap.
        """

        if not heatmap:
            raise ValueError(
                "heatmap cannot be empty."
            )

        # -------------------------------------------------
        # Group Stocks By Sector
        # -------------------------------------------------

        sectors: dict[str, list[HeatmapStock]] = {}

        for stock in heatmap:

            sector = stock.sector.strip()

            if not sector:
                raise ValueError(
                    f"Sector is missing for {stock.symbol}."
                )

            sectors.setdefault(
                sector,
                [],
            ).append(stock)

        # -------------------------------------------------
        # Analyze Each Sector
        # -------------------------------------------------

        results: list[SectorBreadth] = []

        for sector, stocks in sectors.items():

            total_stocks = len(stocks)

            gainers = sum(
                stock.direction == "GAINER"
                for stock in stocks
            )

            losers = sum(
                stock.direction == "LOSER"
                for stock in stocks
            )

            flat = sum(
                stock.direction == "FLAT"
                for stock in stocks
            )

            # ---------------------------------------------
            # Advance / Decline Ratio
            # ---------------------------------------------

            if losers == 0:
                advance_decline_ratio = float(gainers)
            else:
                advance_decline_ratio = (
                    gainers / losers
                )

            # ---------------------------------------------
            # Breadth Percentage
            # ---------------------------------------------

            breadth_pct = (
                (gainers - losers)
                / total_stocks
            ) * 100.0

            # ---------------------------------------------
            # Average Performance
            # ---------------------------------------------

            average_change_pct = (
                sum(
                    stock.change_pct
                    for stock in stocks
                )
                / total_stocks
            )

            # ---------------------------------------------
            # Strongest / Weakest
            # ---------------------------------------------

            strongest = max(
                stocks,
                key=lambda stock: stock.change_pct,
            )

            weakest = min(
                stocks,
                key=lambda stock: stock.change_pct,
            )

            # ---------------------------------------------
            # Result
            # ---------------------------------------------

            results.append(
                SectorBreadth(
                    sector=sector,

                    total_stocks=total_stocks,

                    gainers=gainers,
                    losers=losers,
                    flat=flat,

                    advance_decline_ratio=float(
                        advance_decline_ratio
                    ),

                    breadth_pct=float(
                        breadth_pct
                    ),

                    average_change_pct=float(
                        average_change_pct
                    ),

                    strongest_symbol=strongest.symbol,
                    strongest_change_pct=float(
                        strongest.change_pct
                    ),

                    weakest_symbol=weakest.symbol,
                    weakest_change_pct=float(
                        weakest.change_pct
                    ),
                )
            )

        # Strongest breadth first.
        return sorted(
            results,
            key=lambda item: (
                item.breadth_pct,
                item.average_change_pct,
            ),
            reverse=True,
        )

        # -------------------------------------------------
        # Breadth Counts
        # -------------------------------------------------

        gainers = sum(
            stock.direction == "GAINER"
            for stock in heatmap
        )

        losers = sum(
            stock.direction == "LOSER"
            for stock in heatmap
        )

        flat = sum(
            stock.direction == "FLAT"
            for stock in heatmap
        )

        total_stocks = len(heatmap)

        # -------------------------------------------------
        # Advance / Decline Ratio
        # -------------------------------------------------

        if losers == 0:
            advance_decline_ratio = float(gainers)
        else:
            advance_decline_ratio = (
                gainers / losers
            )

        # -------------------------------------------------
        # Average Change
        # -------------------------------------------------

        average_change_pct = (
            sum(
                stock.change_pct
                for stock in heatmap
            )
            / total_stocks
        )

        # -------------------------------------------------
        # Strongest / Weakest
        # -------------------------------------------------

        strongest = max(
            heatmap,
            key=lambda stock: stock.change_pct,
        )

        weakest = min(
            heatmap,
            key=lambda stock: stock.change_pct,
        )

        # -------------------------------------------------
        # Result
        # -------------------------------------------------

        return HeatmapSummary(
            total_stocks=total_stocks,

            gainers=gainers,
            losers=losers,
            flat=flat,

            advance_decline_ratio=float(
                advance_decline_ratio
            ),

            average_change_pct=float(
                average_change_pct
            ),

            strongest_symbol=strongest.symbol,
            strongest_change_pct=float(
                strongest.change_pct
            ),

            weakest_symbol=weakest.symbol,
            weakest_change_pct=float(
                weakest.change_pct
            ),
        )