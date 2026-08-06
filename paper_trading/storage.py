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
from paper_trading.models import PaperTrade

# =========================================================
# Default Storage
# =========================================================

DEFAULT_STORAGE_FILE = (
    Path("data")
    / "storage"
    / "paper_trades.json"
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

        self._trades: list[PaperTrade] = []

        self._initialize_storage()

        self._load()
        
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

            self._trades = [
                PaperTrade(**item)
                for item in raw
            ]

        except Exception:

            self._trades = []
            
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