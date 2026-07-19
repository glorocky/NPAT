from data.login import GrowwLogin
from data.providers.groww_provider import GrowwProvider


def main():

    print("=" * 60)
    print("NPAT Sprint 1.1 - Expiry Test")
    print("=" * 60)

    # Login
    token = GrowwLogin().get_access_token()

    # Provider
    provider = GrowwProvider(token)

    print("\nFetching NIFTY Expiries...\n")

    expiries = provider.get_expiries(
        exchange="NSE",
        underlying_symbol="NIFTY"
    )

    print(expiries)

    print("\n✅ Expiry Test Passed")


if __name__ == "__main__":
    main()