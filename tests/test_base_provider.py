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
    
    def get_option_chain(
        self,
        exchange: str,
        symbol: str,
        expiry: str | None = None,
    ):
        return []

    def get_greeks(
        self,
        exchange: str,
        symbol: str,
        expiry: str,
        strike: int,
        option_type: str,
    ):
        return None

    def get_market_snapshot(self, symbol, expiry=None):
        return None


        provider = DummyProvider("Dummy")
        info = provider.provider_info()
        assert info["provider"] == "Dummy"
        assert info["class"] == "DummyProvider"

        print("✅ BaseProvider test passed")


