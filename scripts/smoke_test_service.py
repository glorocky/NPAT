from services.paper_trading_service import PaperTradingService

service = PaperTradingService()

print("Open Positions")
print(service.get_open_positions())

print()

print("Trade History")
print(service.get_trade_history())

print()

print("Statistics")
print(service.get_statistics())

print()

print("Summary")
print(service.get_summary())