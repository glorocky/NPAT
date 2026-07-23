import time

from services.cache import cache

print("=" * 60)
print("NPAT CACHE TEST")
print("=" * 60)

cache.set("nifty", 24250, ttl=2)

print(cache.get("nifty"))

time.sleep(3)

print(cache.get("nifty"))

print(cache.stats())