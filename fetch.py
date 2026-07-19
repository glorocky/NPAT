from data.login import GrowwLogin
from growwapi.groww.client import GrowwAPI

token = GrowwLogin().get_access_token()

groww = GrowwAPI(token)
 
 
quote_response = groww.get_quote(
    exchange=groww.EXCHANGE_NSE,
    segment=groww.SEGMENT_CASH,
    trading_symbol="NSE_NIFTY"
)
print(quote_response)