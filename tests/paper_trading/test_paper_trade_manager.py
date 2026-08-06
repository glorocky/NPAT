from pathlib import Path

from paper_trading.enums import (
    TradeSide,
)

from paper_trading.paper_broker import (
    PaperBroker,
)

from paper_trading.storage import (
    PaperTradeStorage,
)

from paper_trading.trade_manager import (
    TradeManager,
)

TEST_FILE = Path(
    "data/storage/test_trade_manager.json"
)

def create_manager():

    if TEST_FILE.exists():
        TEST_FILE.unlink()

    storage = PaperTradeStorage(
        storage_file=TEST_FILE,
    )

    broker = PaperBroker(storage)

    return TradeManager(
        broker,
        storage,
    )
    
def test_manager_initializes():

    manager = create_manager()

    assert manager is not None
    
def test_open_trade():

    manager = create_manager()

    trade = manager.open_trade(
        symbol="NIFTY",
        side=TradeSide.BUY,
        quantity=50,
        price=25000,
    )

    assert trade.symbol == "NIFTY"
    
def test_get_trade():

    manager = create_manager()

    trade = manager.open_trade(
        symbol="NIFTY",
        side=TradeSide.BUY,
        quantity=50,
        price=25000,
    )

    loaded = manager.get_trade(
        trade.trade_id,
    )

    assert loaded is not None

    assert loaded.trade_id == trade.trade_id
    
def test_get_open_trades():

    manager = create_manager()

    manager.open_trade(
        symbol="NIFTY",
        side=TradeSide.BUY,
        quantity=50,
        price=25000,
    )

    assert len(
        manager.get_open_trades()
    ) == 1