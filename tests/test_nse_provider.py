from pprint import pprint

from data.providers.nse_provider import NSEProvider

provider = NSEProvider()

print("=" * 60)

print("Health :", provider.health_check())

print("=" * 60)

snapshot = provider.get_market_snapshot("NIFTY")

print()

pprint(snapshot)