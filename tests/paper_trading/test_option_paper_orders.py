from types import SimpleNamespace

import pytest

from core.models import OptionTradeRecommendation
from paper_trading.enums import ExitReason, TradeStatus
from paper_trading.storage import PaperTradeStorage
from services.paper_trading_service import PaperTradingService


def recommendation(option_type="CE", **overrides):
    values = dict(
        action="BUY CALL" if option_type == "CE" else "BUY PUT",
        option_type=option_type, symbol="NIFTY", expiry="2026-08-27",
        strike_price=25000, entry_price=100.0, spot_price=25000.0,
        confidence=80.0, signal="BUY", reason="test", underlying_symbol="NIFTY",
        exchange="NSE", trading_symbol=f"NIFTY26AUG25000{option_type}", lot_size=25, quantity=25,
    )
    values.update(overrides)
    return OptionTradeRecommendation(**values)


def service(tmp_path, capital=1_000_000):
    return PaperTradingService(PaperTradeStorage(storage_file=tmp_path / "trades.json"), initial_capital=capital)


@pytest.mark.parametrize("option_type", ["CE", "PE"])
def test_confirmed_option_paper_order_persists_exact_contract(tmp_path, option_type):
    paper = service(tmp_path)
    preview = paper.preview_option_order(recommendation(option_type), stop_loss=80, target=140)
    trade = paper.confirm_option_order(preview, confirmed=True)

    assert trade.status is TradeStatus.OPEN
    assert (trade.underlying_symbol, trade.exchange, trade.expiry, trade.strike_price, trade.option_type) == (
        "NIFTY", "NSE", "2026-08-27", 25000, option_type)
    assert trade.trading_symbol.endswith(option_type)
    assert (trade.lot_size, trade.quantity) == (25, 25)


def test_option_order_requires_manual_confirmation(tmp_path):
    paper = service(tmp_path)
    preview = paper.preview_option_order(recommendation(), stop_loss=80, target=140)
    with pytest.raises(PermissionError, match="confirmation"):
        paper.confirm_option_order(preview, confirmed=False)
    assert not paper.get_open_positions()


@pytest.mark.parametrize("field, value", [("trading_symbol", ""), ("lot_size", 0), ("option_type", "XX")])
def test_option_preview_rejects_missing_or_invalid_metadata(tmp_path, field, value):
    paper = service(tmp_path)
    with pytest.raises(ValueError):
        paper.preview_option_order(recommendation(**{field: value}), stop_loss=80, target=140)


def test_option_preview_requires_lot_size_quantity(tmp_path):
    paper = service(tmp_path)
    with pytest.raises(ValueError, match="multiple"):
        paper.preview_option_order(recommendation(), quantity=26, stop_loss=80, target=140)


def test_option_quote_refresh_uses_exact_option_contract(tmp_path):
    paper = service(tmp_path)
    trade = paper.confirm_option_order(
        paper.preview_option_order(recommendation(), stop_loss=80, target=140), confirmed=True)
    calls = []

    def quote_provider(**kwargs):
        calls.append(kwargs)
        return SimpleNamespace(last_price=110.0)

    paper.update_open_market_prices(quote_provider)
    assert calls == [{"symbol": trade.trading_symbol, "exchange": "NSE", "segment": "FNO"}]


@pytest.mark.parametrize("price, reason", [(80.0, ExitReason.STOPLOSS), (140.0, ExitReason.TARGET)])
def test_option_sl_and_target_exits_use_paper_lifecycle(tmp_path, price, reason):
    paper = service(tmp_path)
    trade = paper.confirm_option_order(
        paper.preview_option_order(recommendation(), stop_loss=80, target=140), confirmed=True)
    closed = paper.update_market_price(trade.trade_id, price)
    assert closed.status is TradeStatus.CLOSED
    assert closed.exit_reason is reason


def test_option_order_preserves_existing_capital_risk_limit(tmp_path):
    paper = service(tmp_path, capital=1_000)
    preview = paper.preview_option_order(recommendation(quantity=25), stop_loss=80, target=140)
    with pytest.raises(RuntimeError, match="capital exposure"):
        paper.confirm_option_order(preview, confirmed=True)
