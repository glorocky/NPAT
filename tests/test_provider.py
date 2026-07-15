import os

from dotenv import load_dotenv

from data.providers.groww_provider import GrowwProvider

load_dotenv()

provider = GrowwProvider(
    os.getenv("GROWW_ACCESS_TOKEN")
)

print(provider)

print("\n✅ Provider Initialized Successfully")