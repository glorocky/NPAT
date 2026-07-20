"""
=========================================================
NPAT - NSE API Live Test
=========================================================
"""

from pprint import pprint

from data.utils.http_client import HttpClient
from data.providers.nse.session import NSESessionManager
from data.providers.nse.api import NSEApi


def main():

    print("=" * 70)
    print("NPAT LIVE NSE API TEST")
    print("=" * 70)

    client = HttpClient()
    print("✓ HttpClient created")

    session = NSESessionManager(client)
    print("✓ NSE Session established")

    api = NSEApi(session)
    print("✓ NSE API initialized")

    print("\nChecking API Health...")

    if not api.health_check():
        print("✗ Health Check Failed")
        return

    print("✓ NSE API is reachable")

    print("\nFetching Expiries...")

    expiries = api.get_expiries("NIFTY")

    pprint(expiries)

    expiry = expiries[0]

    print(f"\nNearest Expiry : {expiry}")

    print("\nDownloading Option Chain...")

    option_chain = api.get_option_chain(
        "NIFTY",
        expiry,
    )

    print("✓ Download Successful")

    print("\nSpot Price")
    print(option_chain["underlyingValue"])

    print("\nNumber of Strikes")
    print(len(option_chain["data"]))

    print("\nFirst Strike")

    pprint(option_chain["data"][0])


if __name__ == "__main__":
    main()