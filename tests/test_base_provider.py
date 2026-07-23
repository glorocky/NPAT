from providers.base_provider import BaseProvider


class DummyProvider(BaseProvider):

    def health_check(self):
        return True

    def get_quote(self, symbol):
        return None

    def get_historical_data(self, symbol, interval="5m", period="5d"):
        return []

    def get_expiries(self, symbol):
        return []

    def get_option_chain(self, symbol, expiry=None):
        return []

    def get_market_snapshot(self, symbol, expiry=None):
        return None


provider = DummyProvider("Dummy")
info = provider.provider_info()
assert info["provider"] == "Dummy"
assert info["class"] == "DummyProvider"

print("✅ BaseProvider test passed")


