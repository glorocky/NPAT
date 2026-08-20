"""
=========================================================
NPAT Paper Trading
Storage
=========================================================

Persistent storage for the Paper Trading Engine.

Uses a JSON repository today while remaining
future-ready for SQLite or any database backend.

=========================================================
"""
from __future__ import annotations
import json
from dataclasses import asdict
from pathlib import Path
from paper_trading.models import (
    PaperTrade,
    TradeEvent,
)
from datetime import datetime

from paper_trading.enums import (
    AIRecommendation,
    ExitReason,
    OrderType,
    TradeSide,
    TradeSource,
    TradeStatus,
)

# =========================================================
# Default Storage
# =========================================================

DEFAULT_STORAGE_FILE = (
    Path("data")
    / "storage"
    / "paper_trades.json"
)

DEFAULT_EVENT_STORAGE_FILE = (
    Path("data")
    / "storage"
    / "paper_trade_events.json"
)

# =========================================================
# Storage
# =========================================================

class PaperTradeStorage:
    """
    Repository for all paper trades.
    """

    def __init__(
        self,
        storage_file: Path = DEFAULT_STORAGE_FILE,
    ):

        self.storage_file = storage_file

        self.event_storage_file = (
            self.storage_file.parent
            / "paper_trade_events.json"
        )

        self._trades: list[PaperTrade] = []

        self._events: list[TradeEvent] = []

        self._initialize_storage()

        self._initialize_event_storage()

        self._load()

        self._load_events()
        
    # =========================================================
    # Initialize
    # =========================================================

    def _initialize_storage(
        self,
    ) -> None:
        """
        Create storage file if missing.
        """

        self.storage_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not self.storage_file.exists():

            self.storage_file.write_text(
                "[]",
                encoding="utf-8",
            )  
    
    # =========================================================
    # Initialize Event Storage
    # =========================================================

    def _initialize_event_storage(
        self,
    ) -> None:
        """
        Create event storage file if missing.
        """

        self.event_storage_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not self.event_storage_file.exists():

            self.event_storage_file.write_text(
                "[]",
                encoding="utf-8",
            )
    # =========================================================
    # Public API
    # =========================================================

    def get_all_trades(
        self,
    ) -> list[PaperTrade]:
        """
        Return all paper trades.
        """
        return list(self._trades)

    def get_trade(
        self,
        trade_id: str,
    ) -> PaperTrade | None:
        """
        Return one trade by its ID.
        """
        for trade in self._trades:
            if trade.trade_id == trade_id:
                return trade

        return None

    def get_open_trades(
        self,
    ) -> list[PaperTrade]:
        """
        Return all open paper trades.
        """
        from paper_trading.enums import TradeStatus

        return [
            trade
            for trade in self._trades
            if trade.status == TradeStatus.OPEN
        ]

    def get_closed_trades(
        self,
    ) -> list[PaperTrade]:
        """
        Return all closed paper trades.
        """
        from paper_trading.enums import TradeStatus

        return [
            trade
            for trade in self._trades
            if trade.status == TradeStatus.CLOSED
        ]    
        
    # =========================================================
    # Load
    # =========================================================

    def _load(
        self,
    ) -> None:
        """
        Load trades from storage.
        """

        self._trades = []

        try:

            raw = json.loads(
                self.storage_file.read_text(
                    encoding="utf-8",
                )
            )

            self._trades = []

            for item in raw:

                item["side"] = TradeSide(item["side"])
                item["order_type"] = OrderType(item["order_type"])
                item["source"] = TradeSource(item["source"])
                item["status"] = TradeStatus(item["status"])

                if item["exit_reason"] is not None:
                    item["exit_reason"] = ExitReason(
                        item["exit_reason"]
                    )

                item["ai_recommendation"] = (
                    AIRecommendation(
                        item["ai_recommendation"]
                    )
                )

                item["entry_time"] = datetime.fromisoformat(
                    item["entry_time"]
                )

                if item["exit_time"] is not None:
                    item["exit_time"] = datetime.fromisoformat(
                        item["exit_time"]
                    )

                self._trades.append(
                    PaperTrade(**item)
                )

        except Exception:

            self._trades = []                     
    
    # =========================================================
    # Load Events
    # =========================================================

    def _load_events(
        self,
    ) -> None:
        """
        Load trade lifecycle events from storage.
        """

        self._events = []

        try:

            raw = json.loads(
                self.event_storage_file.read_text(
                    encoding="utf-8",
                )
            )

            for item in raw:

                item["timestamp"] = (
                    datetime.fromisoformat(
                        item["timestamp"]
                    )
                )

                self._events.append(
                    TradeEvent(**item)
                )

        except Exception:

            self._events = []
            
    # =========================================================
    # Save Event
    # =========================================================

    def save_event(
        self,
        event: TradeEvent,
    ) -> None:
        """
        Save one trade lifecycle event.
        """

        self._events.append(event)

        data = [
            asdict(item)
            for item in self._events
        ]

        self.event_storage_file.write_text(
            json.dumps(
                data,
                indent=4,
                default=str,
            ),
            encoding="utf-8",
        )


    # =========================================================
    # Get Events
    # =========================================================

    def get_events(
        self,
        trade_id: str | None = None,
    ) -> list[TradeEvent]:
        """
        Return trade lifecycle events.

        When trade_id is supplied, return only events
        belonging to that trade.
        """

        if trade_id is None:
            return list(self._events)

        return [
            event
            for event in self._events
            if event.trade_id == trade_id
        ]
        
    # =========================================================
    # Flush
    # =========================================================

    def _flush(
        self,
    ) -> None:
        """
        Persist all paper trades to storage.
        """

        data = [
            asdict(trade)
            for trade in self._trades
        ]

        self.storage_file.write_text(
            json.dumps(
                data,
                indent=4,
                default=str,
            ),
            encoding="utf-8",
        )
    
    # =========================================================
    # Save
    # =========================================================

    def save_trade(
        self,
        trade: PaperTrade,
    ) -> None:
        """
        Save a new paper trade.
        """

        self._trades.append(trade)

        self._flush()
        
    # =========================================================
    # Delete
    # =========================================================

    def delete_trade(
        self,
        trade_id: str,
    ) -> bool:
        """
        Delete a paper trade by trade ID.

        Returns True when a trade was deleted,
        otherwise False.
        """

        original_count = len(self._trades)

        self._trades = [
            trade
            for trade in self._trades
            if trade.trade_id != trade_id
        ]

        deleted = (
            len(self._trades) < original_count
        )

        if deleted:
            self._flush()

        return deleted
    
# =========================================================
# Public API
# =========================================================

def get_all_trades(
    self,
) -> list[PaperTrade]:
    """
    Return all paper trades.
    """

    return list(self._trades)


def get_trade(
    self,
    trade_id: str,
) -> PaperTrade | None:
    """
    Return one trade by its ID.
    """

    for trade in self._trades:

        if trade.trade_id == trade_id:
            return trade

    return None


def get_open_trades(
    self,
) -> list[PaperTrade]:
    """
    Return all open paper trades.
    """

    return [
        trade
        for trade in self._trades
        if trade.status.name == "OPEN"
    ]


def get_closed_trades(
    self,
) -> list[PaperTrade]:
    """
    Return all closed paper trades.
    """

    return [
        trade
        for trade in self._trades
        if trade.status.name == "CLOSED"
    ]