from data.providers.yahoo_provider import YahooProvider

provider = YahooProvider()

print("=" * 60)

print("Yahoo Health :", provider.health_check())

print("=" * 60)

print("\nNIFTY Quote")

print(provider.get_quote("NIFTY"))

print("\nBANKNIFTY Quote")

print(provider.get_quote("BANKNIFTY"))

print("\nHistorical Data")

df = provider.get_historical_data(
    "NIFTY",
    interval="5m",
    period="5d",
)

print(df.tail())

print("=" * 60)