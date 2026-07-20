"""
=========================================================
NPAT - NSE Parser Test
=========================================================

Tests:
1. Download Option Chain
2. Parse Option Chain
3. Verify Parsed Objects

Author : Rocky Chopra
=========================================================
"""

from pprint import pprint

from core.models import OptionData
from data.providers.nse.api import NSEApi
from data.providers.nse.parser import NSEParser
from data.providers.nse.session import NSESessionManager
from data.utils.http_client import HttpClient


def main():

    print("=" * 70)
    print("NPAT PARSER TEST")
    print("=" * 70)

    # -----------------------------------------------------
    # Create HTTP Client
    # -----------------------------------------------------

    client = HttpClient()

    # -----------------------------------------------------
    # Create Session
    # -----------------------------------------------------

    session = NSESessionManager(client)

    # -----------------------------------------------------
    # Create API
    # -----------------------------------------------------

    api = NSEApi(session)

    # -----------------------------------------------------
    # Download Option Chain
    # -----------------------------------------------------

    chain = api.get_option_chain("NIFTY")

    print(f"Spot Price : {chain['underlyingValue']}")
    print(f"Raw Strikes : {len(chain['data'])}")

    # -----------------------------------------------------
    # Parse
    # -----------------------------------------------------

    options = NSEParser.parse_option_chain(chain)

    print(f"\nParsed Objects : {len(options)}")

    if not options:
        raise RuntimeError("Parser returned an empty list.")

    print("\nFirst Parsed OptionData\n")

    pprint(options[0])

    # -----------------------------------------------------
    # Validation
    # -----------------------------------------------------

    assert len(options) == len(chain["data"])

    assert isinstance(options[0], OptionData)

    print("\n✓ Parser Test Passed")


if __name__ == "__main__":
    main()