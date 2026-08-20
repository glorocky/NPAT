from services.paper_trading_service import (
    PaperTradingService,
)


service = PaperTradingService()

print("Initial Open Positions")
print(service.get_open_positions())

print()
print("Opening BUY")

trade = service.buy(
    symbol="TEST",
    quantity=1,
    price=100,
)

print(trade)

print()
print("Closing BUY")

closed = service.close_trade(
    trade_id=trade.trade_id,
    price=110,
)

print(closed)

print()
print("Realized P&L")
print(closed.realized_pnl)

print()
print("Final Open Positions")
print(service.get_open_positions())