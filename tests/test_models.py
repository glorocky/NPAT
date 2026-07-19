from datetime import datetime

from core.models import Quote, HistoricalCandle, OptionData, MarketSnapshot


quote = Quote(
    symbol="NIFTY",
    exchange="NSE",
    last_price=25250.45,
    open=25180.00,
    high=25290.20,
    low=25110.00,
    previous_close=25150.35,
    volume=125000,
    timestamp=datetime.now(),
)

print(quote)


candle = HistoricalCandle(
    timestamp=datetime.now(),
    open=100,
    high=110,
    low=99,
    close=108,
    volume=50000,
)

print(candle)


option = OptionData(
    strike=25250,
    call_oi=125000,
    put_oi=98500,
)

print(option)


snapshot = MarketSnapshot(
    symbol="NIFTY",
    spot_price=25250.45,
    expiry="31-Jul-2026",
    atm_strike=25250,
    pcr=1.08,
    support=[25100, 25050],
    resistance=[25300, 25400],
    options=[option],
    timestamp=datetime.now(),
)

print(snapshot)