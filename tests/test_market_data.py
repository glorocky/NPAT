from data.providers.groww_provider import GrowwProvider
import os

ACCESS_TOKEN = os.getenv("GROWW_ACCESS_TOKEN")

provider = GrowwProvider(ACCESS_TOKEN)

print("Connected Successfully")