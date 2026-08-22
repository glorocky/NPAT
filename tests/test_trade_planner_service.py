from services.market_service import MarketService
from core.models import Quote, FutureData, OptionData


class FakeProvider:
    def get_quote(self, trading_symbol, exchange, segment):
        return Quote(
            symbol=trading_symbol,
            exchange=exchange,
            last_price=100.0,
            open=99.0,
            high=102.0,
            low=98.0,
            previous_close=99.0,
        )

    def get_future(self, symbol, exchange):
        return FutureData(
            symbol=symbol,
            exchange=exchange,
            trading_symbol=f"{symbol}FUT",
            expiry="2099-09-29",
            lot_size=65,
            last_price=101.0,
            open=100.0,
            high=102.0,
            low=98.0,
            previous_close=99.0,
            open_interest=1100,
            previous_open_interest=1000,
            oi_change=100,
        )

    def get_expiries(self, exchange, underlying_symbol):
        return ["2099-09-29"]

    def get_option_chain(self, exchange, symbol, expiry):
        return [
            OptionData(
                strike_price=100,
                expiry=expiry,
                underlying_price=100.0,
                put_ltp=3.0,
                put_trading_symbol=f"{symbol}100PE",
                put_lot_size=65,
            ),
            OptionData(
                strike_price=105,
                expiry=expiry,
                underlying_price=100.0,
                call_ltp=2.5,
                call_trading_symbol=f"{symbol}105CE",
                call_lot_size=65,
            ),
        ]


def _service():
    service = object.__new__(MarketService)
    service.provider = FakeProvider()
    return service


def test_future_trade_plan_adds_protective_put():
    idea = _service().get_hedged_trade_idea("FUTURE", "NIFTY", 1, 40)
    assert idea.action == "BUY FUTURE"
    assert idea.hedge is not None
    assert idea.hedge.option_type == "PE"
    assert idea.hedge.action == "BUY PUT"
    assert idea.hedge.quantity == 65


def test_short_stock_trade_plan_uses_call_hedge():
    service = _service()
    original = service.provider.get_quote
    service.provider.get_quote = lambda trading_symbol, exchange, segment: Quote(
        symbol=trading_symbol, exchange=exchange, last_price=98.0,
        open=100.0, high=101.0, low=97.0, previous_close=100.0,
    )
    idea = service.get_hedged_trade_idea("STOCK", "RELIANCE", 100, -40)
    assert idea.action == "SELL STOCK"
    assert idea.hedge is not None
    assert idea.hedge.option_type == "CE"
    assert idea.hedge.action == "BUY CALL"
