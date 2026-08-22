"""
=========================================================
NPAT
Paper Trading Service
=========================================================

Service layer between the dashboard and the
Paper Trading Engine.

Responsibilities

• Portfolio Summary
• Open Positions
• Trade History
• Performance Statistics
• Buy / Sell
• Close Trade

No business logic should exist here.

=========================================================
"""
from __future__ import annotations

from paper_trading.trade_manager import TradeManager
from paper_trading.storage import PaperTradeStorage
from paper_trading.paper_broker import PaperBroker
from paper_trading.performance import PerformanceEngine
from paper_trading.position_manager import PositionManager
from config import (
    PAPER_TRADING_INITIAL_CAPITAL,
    PAPER_TRADING_MAX_DAILY_LOSS,
    PAPER_TRADING_MAX_OPEN_TRADES,
    PAPER_TRADING_MAX_CAPITAL_EXPOSURE_PCT,
)
from paper_trading.models import (
    DashboardSummary,
    OptionPaperOrderPreview,
    TradeEvent,
)

from paper_trading.enums import (
    TradeSide,
    TradeSource,
    ExitReason,
)


class PaperTradingService:

    def __init__(
        self,
        storage: PaperTradeStorage | None = None,
        initial_capital: float = PAPER_TRADING_INITIAL_CAPITAL,
    ):
                 

        self.storage = storage or PaperTradeStorage()
        self.initial_capital = float(initial_capital)
        
        self.max_daily_loss = float(
        PAPER_TRADING_MAX_DAILY_LOSS
        )

        self.max_open_trades = int(
        PAPER_TRADING_MAX_OPEN_TRADES
        )
        
        self.max_capital_exposure_pct = float(
        PAPER_TRADING_MAX_CAPITAL_EXPOSURE_PCT
        )

        self.broker = PaperBroker(
            self.storage,
        )

        self.trade_manager = TradeManager(
            self.broker,
            self.storage,
        )

        self.performance = PerformanceEngine()
        
    # =========================================================
    # Trade Event
    # =========================================================

    def _record_event(
        self,
        trade_id: str,
        event: str,
        description: str,
    ) -> None:
        """
        Record one trade lifecycle event.
        """

        trade_event = TradeEvent(
            trade_id=trade_id,
            event=event,
            description=description,
        )

        self.storage.save_event(
            trade_event,
        )

        self.position_manager = PositionManager()
    # =========================================================
    # Open Positions
    # =========================================================

    def get_open_positions(self):
        """
        Return all open paper trades.
        """

        return self.trade_manager.get_open_trades()
    
    # =========================================================
    # Trade History
    # =========================================================

    def get_trade_history(self):
        """
        Return all paper trades.
        """

        return self.storage.get_all_trades()
    
    # =========================================================
    # Trade Events
    # =========================================================

    def get_trade_events(
        self,
        trade_id: str | None = None,
    ):
        """
        Return paper trading lifecycle events.
        """

        return self.storage.get_events(
            trade_id=trade_id,
        )
        
    # =========================================================
    # Statistics
    # =========================================================

    def get_statistics(
        self,
    ):
        """
        Return paper trading statistics.
        """

        trades = self.storage.get_all_trades()

        return self.performance.calculate_statistics(
            trades,
        )
        
    # =========================================================
    # Equity Curve
    # =========================================================

    def get_equity_curve(
        self,
    ) -> list[float]:
        """
        Return cumulative realized P&L after each
        closed paper trade.
        """

        trades = self.storage.get_all_trades()

        return self.performance.calculate_equity_curve(
            trades,
        )
        
    # =========================================================
    # Dashboard Summary
    # =========================================================
    def get_summary(
    self,
    ) -> DashboardSummary:
        """
        Return the Paper Trading dashboard summary.
        """

        trades = self.storage.get_all_trades()

        statistics = self.performance.calculate_statistics(
            trades,
        )

        open_trades = self.storage.get_open_trades()

        closed_trades = self.storage.get_closed_trades()

        total_pnl = sum(
            trade.realized_pnl
            for trade in trades
        )

        from datetime import datetime, timezone

        today = datetime.now(
            timezone.utc
        ).date()

        today_pnl = sum(
            trade.realized_pnl
            for trade in closed_trades
            if trade.exit_time is not None
            and trade.exit_time.date() == today
        )

        capital_committed = sum(
        trade.entry_price * trade.quantity
        for trade in open_trades
    )

        account_balance = (
            self.initial_capital + total_pnl
        )

        available_cash = (
            account_balance - capital_committed
        )

        return DashboardSummary(

            account_balance=account_balance,

            available_cash=available_cash,

            open_positions=len(open_trades),

            open_trades=len(open_trades),

            closed_trades=len(closed_trades),

            today_pnl=today_pnl,

            total_pnl=total_pnl,

            win_rate=statistics.win_rate,
        )
        
    # =========================================================
    # Daily Loss Risk Check
    # =========================================================

    def _check_daily_loss_limit(self) -> None:
        """
        Prevent new paper trades when the realized daily
        loss reaches the configured maximum daily loss.
        """

        trades = self.storage.get_closed_trades()

        from datetime import datetime, timezone

        today = datetime.now(
            timezone.utc
        ).date()

        today_pnl = sum(
            trade.realized_pnl
            for trade in trades
            if (
                trade.exit_time is not None
                and trade.exit_time.date() == today
            )
        )

        if today_pnl <= -self.max_daily_loss:
            raise RuntimeError(
                "Paper trading daily loss limit reached. "
                f"Today's P&L: ₹{today_pnl:,.2f}. "
                f"Maximum daily loss: "
                f"₹{self.max_daily_loss:,.2f}."
            )
            
    # =========================================================
    # Maximum Open Trades Risk Check
    # =========================================================

    def _check_max_open_trades(self) -> None:
        """
        Prevent new paper trades when the configured
        maximum number of open trades has been reached.
        """

        open_trades = self.storage.get_open_trades()

        if len(open_trades) >= self.max_open_trades:
            raise RuntimeError(
                "Paper trading maximum open trades limit reached. "
                f"Open trades: {len(open_trades)}. "
                f"Maximum allowed: {self.max_open_trades}."
            )
         
    # =========================================================
    # Capital Exposure
    # =========================================================

    def _get_capital_exposure(self) -> float:
        """
        Return the total entry-value exposure of all
        currently open paper trades.
        """

        open_trades = self.storage.get_open_trades()

        return sum(
            trade.entry_price * trade.quantity
            for trade in open_trades
        )  
        
    
    # =========================================================
    # Maximum Capital Exposure Risk Check
    # =========================================================

    def _check_capital_exposure(
        self,
        price: float,
        quantity: int,
    ) -> None:
        """
        Prevent a new paper trade from exceeding
        the configured maximum capital exposure.
        """

        current_exposure = self._get_capital_exposure()

        account_balance = (
            self.initial_capital
            + sum(
                trade.realized_pnl
                for trade in self.storage.get_all_trades()
            )
        )

        max_exposure = (
            account_balance
            * self.max_capital_exposure_pct
            / 100.0
        )

        new_trade_exposure = price * quantity

        total_exposure = (
            current_exposure
            + new_trade_exposure
        )

        if total_exposure > max_exposure:
            raise RuntimeError(
                "Paper trading maximum capital exposure "
                "limit reached. "
                f"Current exposure: "
                f"₹{current_exposure:,.2f}. "
                f"New trade exposure: "
                f"₹{new_trade_exposure:,.2f}. "
                f"Total exposure: "
                f"₹{total_exposure:,.2f}. "
                f"Maximum allowed: "
                f"₹{max_exposure:,.2f}."
            )     
   
    # =========================================================
    # Buy
    # =========================================================

    def buy(
        self,
        symbol: str,
        quantity: int,
        price: float,
        stop_loss: float = 0.0,
        target: float = 0.0,
    ) -> object:
        """
        Open a manual BUY paper trade.
        """
        
        self._check_daily_loss_limit()
        self._check_max_open_trades()
        
        self._check_capital_exposure(
        price=price,
        quantity=quantity,
    )

        trade = self.trade_manager.open_trade(
            symbol=symbol,
            side=TradeSide.BUY,
            quantity=quantity,
            price=price,
            stop_loss=stop_loss,
            target=target,
            source=TradeSource.MANUAL,
        )
        self._record_event(
        trade_id=trade.trade_id,
        event="TRADE_OPENED",
        description=(
            f"Manual BUY opened at "
        f"₹{price:,.2f}, quantity {quantity}."
        ),
    )

        return trade

    # =========================================================
    # AI Option Paper Orders
    # =========================================================

    @staticmethod
    def _validate_option_recommendation(recommendation, quantity: int) -> None:
        required_text = {
            "underlying symbol": recommendation.underlying_symbol,
            "exchange": recommendation.exchange,
            "expiry": recommendation.expiry,
            "option type": recommendation.option_type,
            "trading symbol": recommendation.trading_symbol,
        }
        missing = [name for name, value in required_text.items() if not str(value).strip()]
        if missing:
            raise ValueError("Option recommendation is missing " + ", ".join(missing) + ".")
        if recommendation.option_type not in {"CE", "PE"}:
            raise ValueError("Option recommendation type must be CE or PE.")
        if recommendation.action not in {"BUY CALL", "BUY PUT"}:
            raise ValueError("Option recommendation is not a buyable option trade.")
        if recommendation.entry_price <= 0 or recommendation.strike_price <= 0:
            raise ValueError("Option recommendation has an invalid entry price or strike.")
        if recommendation.lot_size <= 0:
            raise ValueError("Option recommendation has an invalid lot size.")
        if quantity <= 0 or quantity % recommendation.lot_size:
            raise ValueError("Option quantity must be a positive multiple of the lot size.")

    def preview_option_order(self, recommendation, *, quantity: int | None = None,
                             stop_loss: float = 0.0, target: float = 0.0) -> OptionPaperOrderPreview:
        """Build a non-executable paper order preview from an AI recommendation."""
        order_quantity = int(recommendation.quantity if quantity is None else quantity)
        self._validate_option_recommendation(recommendation, order_quantity)
        entry = float(recommendation.entry_price)
        if stop_loss <= 0 or target <= 0 or stop_loss >= entry or target <= entry:
            raise ValueError("Option stop loss must be below entry and target must be above entry.")
        risk_reward = (target - entry) / (entry - stop_loss)
        return OptionPaperOrderPreview(
            underlying_symbol=recommendation.underlying_symbol,
            exchange=recommendation.exchange,
            expiry=recommendation.expiry,
            strike_price=int(recommendation.strike_price),
            option_type=recommendation.option_type,
            trading_symbol=recommendation.trading_symbol,
            entry_price=entry,
            lot_size=int(recommendation.lot_size),
            quantity=order_quantity,
            stop_loss=float(stop_loss),
            target=float(target),
            risk_reward=risk_reward,
        )

    def confirm_option_order(self, preview: OptionPaperOrderPreview, *, confirmed: bool) -> object:
        """Create an AI option paper order only after explicit user confirmation."""
        if not confirmed:
            raise PermissionError("Explicit manual confirmation is required for a paper option order.")
        self._check_daily_loss_limit()
        self._check_max_open_trades()
        self._check_capital_exposure(preview.entry_price, preview.quantity)
        trade = self.trade_manager.open_trade(
            symbol=preview.underlying_symbol,
            side=TradeSide.BUY,
            quantity=preview.quantity,
            price=preview.entry_price,
            stop_loss=preview.stop_loss,
            target=preview.target,
            source=TradeSource.AI,
            underlying_symbol=preview.underlying_symbol,
            exchange=preview.exchange,
            expiry=preview.expiry,
            strike_price=preview.strike_price,
            option_type=preview.option_type,
            trading_symbol=preview.trading_symbol,
            lot_size=preview.lot_size,
        )
        self._record_event(
            trade.trade_id,
            "OPTION_PAPER_ORDER_OPENED",
            f"Confirmed {preview.option_type} {preview.trading_symbol} @ {preview.entry_price:,.2f}, quantity {preview.quantity}.",
        )
        return trade
        
    # =========================================================
    # AI Auto Paper Execution
    # =========================================================

    def auto_execute_ai(self, ai_result, *, decision_key: str) -> dict:
        """
        Automatically open an AI paper option trade once for a given
        decision key.  This is paper-trading only; no live broker order
        is placed.

        The method accepts the AI result object used by the dashboard/tests
        (``recommendation``, ``signal``, ``confidence`` and ``reasons``).
        A decision key prevents the same AI decision from opening duplicate
        paper positions during repeated dashboard refreshes.
        """
        if not hasattr(self, "_ai_processed_decisions"):
            self._ai_processed_decisions: set[str] = set()

        key = str(decision_key or "").strip()
        if not key:
            raise ValueError("AI decision_key is required.")

        if key in self._ai_processed_decisions:
            return {"status": "ALREADY_PROCESSED"}

        recommendation = getattr(ai_result, "recommendation", None)
        action = str(getattr(recommendation, "action", "")).strip().upper()

        if action == "NO TRADE":
            self._ai_processed_decisions.add(key)
            return {"status": "NO_TRADE"}

        # Only the existing AI option recommendations are eligible for
        # automatic paper execution.  Manual/live execution is untouched.
        quantity = int(getattr(recommendation, "quantity", 0) or 0)
        self._validate_option_recommendation(recommendation, quantity)

        self._check_daily_loss_limit()
        self._check_max_open_trades()

        entry = float(recommendation.entry_price)
        # Default AI-paper risk profile used by Sprint 12 tests/planner:
        # 20% protective stop and 35% upside target from option entry.
        stop_loss = round(entry * 0.80, 10)
        target = round(entry * 1.35, 10)
        self._check_capital_exposure(entry, quantity)

        trade = self.trade_manager.open_trade(
            symbol=recommendation.underlying_symbol,
            side=TradeSide.BUY,
            quantity=quantity,
            price=entry,
            stop_loss=stop_loss,
            target=target,
            source=TradeSource.AI,
            underlying_symbol=recommendation.underlying_symbol,
            exchange=recommendation.exchange,
            expiry=recommendation.expiry,
            strike_price=int(recommendation.strike_price),
            option_type=recommendation.option_type,
            trading_symbol=recommendation.trading_symbol,
            lot_size=int(recommendation.lot_size),
        )

        self._ai_processed_decisions.add(key)
        self._record_event(
            trade.trade_id,
            "AI_AUTO_PAPER_OPENED",
            (
                f"AI {recommendation.action} opened {recommendation.trading_symbol} "
                f"@ {entry:,.2f}, quantity {quantity}, "
                f"confidence {float(getattr(ai_result, 'confidence', 0.0)):,.1f}%."
            ),
        )

        return {"status": "OPENED", "trade": trade}

    # =========================================================
    # Update Market Price
    # =========================================================

    def update_market_price(
        self,
        trade_id: str,
        price: float,
    ) -> object:
        """
        Update the market price of an open paper trade.
        """

        return self.trade_manager.update_market_price(
            trade_id=trade_id,
            price=price,
        )
    
    # =========================================================
    # Update All Open Market Prices
    # =========================================================

    def update_open_market_prices(
        self,
        quote_provider,
    ) -> list[object]:
        """
        Update all open paper trades using a supplied quote provider.

        The quote provider is responsible for retrieving the
        latest market quote. The paper trading engine only
        receives the resulting price.
        """

        updated_trades = []

        open_trades = self.get_open_positions()

        for trade in open_trades:

            quote = quote_provider(
                symbol=trade.trading_symbol or trade.symbol,
                exchange=trade.exchange,
                segment="FNO" if trade.trading_symbol else "CASH",
            )

            updated_trade = self.update_market_price(
                trade_id=trade.trade_id,
                price=float(quote.last_price),
            )

            updated_trades.append(updated_trade)

        return updated_trades


    # =========================================================
    # Sell
    # =========================================================

    def sell(
        self,
        symbol: str,
        quantity: int,
        price: float,
        stop_loss: float = 0.0,
        target: float = 0.0,
    ) -> object:
        """
        Open a manual SELL paper trade.
        """
        
        self._check_daily_loss_limit()
        self._check_max_open_trades()
        
        self._check_capital_exposure(
        price=price,
        quantity=quantity,
    )

        trade = self.trade_manager.open_trade(
            symbol=symbol,
            side=TradeSide.SELL,
            quantity=quantity,
            price=price,
            stop_loss=stop_loss,
            target=target,
            source=TradeSource.MANUAL,
        )
        self._record_event(
            trade_id=trade.trade_id,
            event="TRADE_OPENED",
            description=(
                f"Manual SELL opened at "
                f"₹{price:,.2f}, quantity {quantity}."
            ),
        )
        return trade

    # =========================================================
    # Close Trade
    # =========================================================

    def close_trade(
        self,
        trade_id: str,
        price: float,
        exit_reason: ExitReason = ExitReason.MANUAL,
    ) -> object:
        """
        Close an existing paper trade.
        """
        return self.trade_manager.close_trade(
            trade_id=trade_id,
            price=price,
            exit_reason=exit_reason,
        )
        
        col6.metric(
        "Max Drawdown",
        f"₹ {statistics.max_drawdown:,.2f}",
        )