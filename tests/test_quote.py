from data.login import GrowwLogin
from data.providers.groww_provider import GrowwProvider

token = GrowwLogin().get_access_token()
provider = GrowwProvider(token)

quote = provider.get_quote(
    trading_symbol="NIFTY",
    exchange="NSE",
    segment="CASH"
)

print(quote)