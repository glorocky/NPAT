from paper_trading.storage import PaperTradeStorage
from paper_trading.models import PaperTrade
from paper_trading.enums import TradeStatus
from pathlib import Path

TEST_FILE = Path("data/storage/test_paper_storage.json")


def create_storage():

    if TEST_FILE.exists():
        TEST_FILE.unlink()

    return PaperTradeStorage(
        storage_file=TEST_FILE,
    )


def test_storage_initializes():

    storage = create_storage()

    assert storage is not None
    
def test_get_all_trades():

    storage = create_storage()

    assert isinstance(
        storage.get_all_trades(),
        list,
    )
    
def test_get_trade():

    storage = create_storage()

    trade = PaperTrade(
        symbol="NIFTY"
    )

    storage.save_trade(trade)

    result = storage.get_trade(
        trade.trade_id
    )

    assert result is trade

def test_get_open_trades():

    storage = create_storage()

    trade = PaperTrade(
        status=TradeStatus.OPEN,
    )

    storage.save_trade(trade)

    assert len(storage.get_open_trades()) == 1
    
def test_get_closed_trades():

    storage = create_storage()

    trade = PaperTrade(
        status=TradeStatus.CLOSED
    )

    storage.save_trade(trade)

    assert len(
        storage.get_closed_trades()
    ) == 1
    
def test_save_trade():

    storage = create_storage()

    initial_count = len(
        storage.get_all_trades()
    )

    trade = PaperTrade(
        symbol="NIFTY",
    )

    storage.save_trade(trade)

    assert len(
        storage.get_all_trades()
    ) == initial_count + 1