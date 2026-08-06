
from pathlib import Path

from paper_trading.enums import (
    TradeSide,
    TradeStatus,
)

from paper_trading.paper_broker import (
    PaperBroker,
)

from paper_trading.storage import (
    PaperTradeStorage,
)

TEST_FILE = Path("data/storage/test_paper_trades.json")
def test_broker_initializes():
    
    if TEST_FILE.exists():
        TEST_FILE.unlink()

    storage = PaperTradeStorage(
        storage_file=TEST_FILE,
    )

    broker = PaperBroker(storage)

    assert broker is not None
    
def test_place_order():
    
    if TEST_FILE.exists():
        TEST_FILE.unlink()

    storage = PaperTradeStorage(
        storage_file=TEST_FILE,
    )
    

    broker = PaperBroker(storage)

    trade = broker.place_order(
        symbol="NIFTY",
        side=TradeSide.BUY,
        quantity=50,
        price=25000,
    )

    assert trade.status == TradeStatus.OPEN

    assert trade.entry_price == 25000
    
def test_trade_saved():

    if TEST_FILE.exists():
        TEST_FILE.unlink()

    storage = PaperTradeStorage(
        storage_file=TEST_FILE,
    )
    

    initial_count = len(
        storage.get_all_trades()
    )

    broker = PaperBroker(storage)

    broker.place_order(
        symbol="NIFTY",
        side=TradeSide.BUY,
        quantity=50,
        price=25000,
    )

    assert len(
        storage.get_all_trades()
    ) == initial_count + 1