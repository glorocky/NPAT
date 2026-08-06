"""
=========================================================
NPAT Paper Trading
Performance Engine
=========================================================

Calculates paper trading performance statistics.

This module is intentionally stateless.

=========================================================
"""

from __future__ import annotations

from paper_trading.models import (
    PaperTrade,
    TradeStatistics,
)


# =========================================================
# Performance Engine
# =========================================================

class PerformanceEngine:
    """
    Calculates paper trading performance.
    """

    # =====================================================
    # Total Trades
    # =====================================================

    @staticmethod
    def calculate_total_trades(
        trades: list[PaperTrade],
    ) -> int:

        return len(trades)

    # =====================================================
    # Winning Trades
    # =====================================================

    @staticmethod
    def calculate_winning_trades(
        trades: list[PaperTrade],
    ) -> int:

        return sum(
            1
            for trade in trades
            if trade.realized_pnl > 0
        )

    # =====================================================
    # Losing Trades
    # =====================================================

    @staticmethod
    def calculate_losing_trades(
        trades: list[PaperTrade],
    ) -> int:

        return sum(
            1
            for trade in trades
            if trade.realized_pnl < 0
        )

    # =====================================================
    # Win Rate
    # =====================================================

    @staticmethod
    def calculate_win_rate(
        trades: list[PaperTrade],
    ) -> float:

        total = len(trades)

        if total == 0:
            return 0.0

        wins = (
            PerformanceEngine.calculate_winning_trades(
                trades
            )
        )

        return (wins / total) * 100

    # =====================================================
    # Statistics
    # =====================================================

    @staticmethod
    def calculate_statistics(
        trades: list[PaperTrade],
    ) -> TradeStatistics:

        return TradeStatistics(
            total_trades=PerformanceEngine.calculate_total_trades(
                trades,
            ),
            winning_trades=PerformanceEngine.calculate_winning_trades(
                trades,
            ),
            losing_trades=PerformanceEngine.calculate_losing_trades(
                trades,
            ),
            win_rate=PerformanceEngine.calculate_win_rate(
                trades,
            ),
        )