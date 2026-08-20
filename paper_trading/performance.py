"""
Calculates paper trading performance statistics.

This module is intentionally stateless.

=========================================================
"""

from __future__ import annotations

from paper_trading.models import (
    PaperTrade,
    TradeStatistics,
)

from paper_trading.enums import TradeStatus


# =========================================================
# Performance Engine
# =========================================================

class PerformanceEngine:
    """
    Calculates paper trading performance.
    """

    # =====================================================
    # Closed Trades
    # =====================================================

    @staticmethod
    def _closed_trades(
        trades: list[PaperTrade],
    ) -> list[PaperTrade]:

        return [
            trade
            for trade in trades
            if trade.status == TradeStatus.CLOSED
        ]

    # =====================================================
    # Total Trades
    # =====================================================

    @staticmethod
    def calculate_total_trades(
        trades: list[PaperTrade],
    ) -> int:

        return len(
            PerformanceEngine._closed_trades(trades)
        )

    # =====================================================
    # Winning Trades
    # =====================================================

    @staticmethod
    def calculate_winning_trades(
        trades: list[PaperTrade],
    ) -> int:

        closed_trades = (
            PerformanceEngine._closed_trades(trades)
        )

        return sum(
            1
            for trade in closed_trades
            if trade.realized_pnl > 0
        )

    # =====================================================
    # Losing Trades
    # =====================================================

    @staticmethod
    def calculate_losing_trades(
        trades: list[PaperTrade],
    ) -> int:

        closed_trades = (
            PerformanceEngine._closed_trades(trades)
        )

        return sum(
            1
            for trade in closed_trades
            if trade.realized_pnl < 0
        )
        
    
    # =====================================================
    # Breakeven Trades
    # =====================================================

    @staticmethod
    def calculate_breakeven_trades(
        trades: list[PaperTrade],
    ) -> int:

        closed_trades = (
            PerformanceEngine._closed_trades(trades)
        )

        return sum(
            1
            for trade in closed_trades
            if trade.realized_pnl == 0
        )

    # =====================================================
    # Win Rate
    # =====================================================

    @staticmethod
    def calculate_win_rate(
        trades: list[PaperTrade],
    ) -> float:

        wins = (
            PerformanceEngine.calculate_winning_trades(
                trades
            )
        )

        losses = (
            PerformanceEngine.calculate_losing_trades(
                trades
            )
        )

        completed = wins + losses

        if completed == 0:
            return 0.0

        return (wins / completed) * 100

    # =====================================================
    # Gross Profit
    # =====================================================

    @staticmethod
    def calculate_gross_profit(
        trades: list[PaperTrade],
    ) -> float:

        closed_trades = (
            PerformanceEngine._closed_trades(trades)
        )

        return sum(
            trade.realized_pnl
            for trade in closed_trades
            if trade.realized_pnl > 0
        )

    # =====================================================
    # Gross Loss
    # =====================================================

    @staticmethod
    def calculate_gross_loss(
        trades: list[PaperTrade],
    ) -> float:

        closed_trades = (
            PerformanceEngine._closed_trades(trades)
        )

        return abs(
        sum(
            trade.realized_pnl
            for trade in trades
            if trade.realized_pnl < 0
        )
    )

    # =====================================================
    # Net Profit
    # =====================================================

    @staticmethod
    def calculate_net_profit(
        trades: list[PaperTrade],
    ) -> float:

        gross_profit = (
            PerformanceEngine.calculate_gross_profit(
                trades
            )
        )

        gross_loss = (
            PerformanceEngine.calculate_gross_loss(
                trades
            )
        )

        return gross_profit - gross_loss

    # =====================================================
    # Average Profit
    # =====================================================

    @staticmethod
    def calculate_average_profit(
        trades: list[PaperTrade],
    ) -> float:

        winners = [
            trade.realized_pnl
            for trade in PerformanceEngine._closed_trades(
                trades
            )
            if trade.realized_pnl > 0
        ]

        if not winners:
            return 0.0

        return sum(winners) / len(winners)

    # =====================================================
    # Average Loss
    # =====================================================

    @staticmethod
    def calculate_average_loss(
        trades: list[PaperTrade],
    ) -> float:

        losers = [
            trade.realized_pnl
            for trade in PerformanceEngine._closed_trades(
                trades
            )
            if trade.realized_pnl < 0
        ]

        if not losers:
            return 0.0

        return sum(losers) / len(losers)

    # =====================================================
    # Largest Win
    # =====================================================

    @staticmethod
    def calculate_largest_win(
        trades: list[PaperTrade],
    ) -> float:

        winners = [
            trade.realized_pnl
            for trade in PerformanceEngine._closed_trades(
                trades
            )
            if trade.realized_pnl > 0
        ]

        if not winners:
            return 0.0

        return max(winners)

    # =====================================================
    # Largest Loss
    # =====================================================

    @staticmethod
    def calculate_largest_loss(
        trades: list[PaperTrade],
    ) -> float:

        losers = [
            trade.realized_pnl
            for trade in PerformanceEngine._closed_trades(
                trades
            )
            if trade.realized_pnl < 0
        ]

        if not losers:
            return 0.0

        return min(losers)

    # =====================================================
    # Profit Factor
    # =====================================================

    @staticmethod
    def calculate_profit_factor(
        trades: list[PaperTrade],
    ) -> float:

        gross_profit = (
            PerformanceEngine.calculate_gross_profit(
                trades
            )
        )

        gross_loss = (
            PerformanceEngine.calculate_gross_loss(
                trades
            )
        )

        if gross_loss == 0:

            if gross_profit > 0:
                return float("inf")

            return 0.0

        return gross_profit / abs(gross_loss)

    # =====================================================
    # Expectancy
    # =====================================================

    @staticmethod
    def calculate_expectancy(
        trades: list[PaperTrade],
    ) -> float:

        total = (
            PerformanceEngine.calculate_total_trades(
                trades
            )
        )

        if total == 0:
            return 0.0

        net_profit = (
            PerformanceEngine.calculate_net_profit(
                trades
            )
        )

        return net_profit / total
    
    # =====================================================
    # Equity Curve
    # =====================================================

    @staticmethod
    def calculate_equity_curve(
        trades: list[PaperTrade],
    ) -> list[float]:
        """
        Calculate cumulative realized P&L after each
        closed trade.

        Returns
        -------
        list[float]
            Cumulative realized P&L values ordered by
            trade exit time.
        """

        closed_trades = (
            PerformanceEngine._closed_trades(trades)
        )

        if not closed_trades:
            return []

        closed_trades = sorted(
            closed_trades,
            key=lambda trade: (
                trade.exit_time
                if trade.exit_time is not None
                else trade.entry_time
            ),
        )

        cumulative_pnl = 0.0
        equity_curve = []

        for trade in closed_trades:

            cumulative_pnl += trade.realized_pnl

            equity_curve.append(
                cumulative_pnl
            )

        return equity_curve
    
    # =====================================================
    # Maximum Drawdown
    # =====================================================

    @staticmethod
    def calculate_max_drawdown(
        trades: list[PaperTrade],
    ) -> float:
        """
        Calculate maximum drawdown from realized P&L.

        Drawdown is measured from the highest cumulative
        realized P&L reached to a subsequent lower value.
        """

        closed_trades = (
            PerformanceEngine._closed_trades(trades)
        )

        if not closed_trades:
            return 0.0

        closed_trades = sorted(
            closed_trades,
            key=lambda trade: (
                trade.exit_time
                if trade.exit_time is not None
                else trade.entry_time
            ),
        )

        cumulative_pnl = 0.0
        peak_pnl = 0.0
        max_drawdown = 0.0

        for trade in closed_trades:

            cumulative_pnl += trade.realized_pnl

            peak_pnl = max(
                peak_pnl,
                cumulative_pnl,
            )

            drawdown = (
                peak_pnl - cumulative_pnl
            )

            max_drawdown = max(
                max_drawdown,
                drawdown,
            )

        return max_drawdown

    # =====================================================
    # Statistics
    # =====================================================

    @staticmethod
    def calculate_statistics(
        trades: list[PaperTrade],
    ) -> TradeStatistics:

        return TradeStatistics(

            total_trades=(
                PerformanceEngine.calculate_total_trades(
                    trades
                )
            ),

            winning_trades=(
                PerformanceEngine.calculate_winning_trades(
                    trades
                )
            ),

            losing_trades=(
                PerformanceEngine.calculate_losing_trades(
                    trades
                )
            ),
            
            breakeven_trades=(
                PerformanceEngine.calculate_breakeven_trades(
                    trades
                )
            ),

            win_rate=(
                PerformanceEngine.calculate_win_rate(
                    trades
                )
            ),

            gross_profit=(
                PerformanceEngine.calculate_gross_profit(
                    trades
                )
            ),

            gross_loss=(
                PerformanceEngine.calculate_gross_loss(
                    trades
                )
            ),

            net_profit=(
                PerformanceEngine.calculate_net_profit(
                    trades
                )
            ),

            average_profit=(
                PerformanceEngine.calculate_average_profit(
                    trades
                )
            ),

            average_loss=(
                PerformanceEngine.calculate_average_loss(
                    trades
                )
            ),

            largest_win=(
                PerformanceEngine.calculate_largest_win(
                    trades
                )
            ),

            largest_loss=(
                PerformanceEngine.calculate_largest_loss(
                    trades
                )
            ),

            profit_factor=(
                PerformanceEngine.calculate_profit_factor(
                    trades
                )
            ),

            expectancy=(
                PerformanceEngine.calculate_expectancy(
                    trades
                )
            ),
            
            max_drawdown=(
            PerformanceEngine.calculate_max_drawdown(
                trades
                )
            ),
        )