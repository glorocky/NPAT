"""
============================================================
NPAT RATE LIMITER TEST
============================================================
"""

import time

from services.exceptions import RateLimitExceededException
from services.rate_limiter import RateLimiter


print("=" * 60)
print("NPAT RATE LIMITER TEST")
print("=" * 60)

# ---------------------------------------------------------
# Create limiter
# ---------------------------------------------------------

limiter = RateLimiter(
    capacity=3,
    refill_rate=1,
)

print("\nInitial")
print(limiter.stats())

# ---------------------------------------------------------
# Consume all tokens
# ---------------------------------------------------------

print("\nConsuming tokens...")

limiter.acquire()
print(limiter.stats())

limiter.acquire()
print(limiter.stats())

limiter.acquire()
print(limiter.stats())

# ---------------------------------------------------------
# Should fail now
# ---------------------------------------------------------

print("\nTesting rate limit...")

try:

    limiter.acquire()

except RateLimitExceededException:

    print("Rate limit correctly enforced.")

else:

    raise AssertionError(
        "Expected RateLimitExceededException."
    )

# ---------------------------------------------------------
# Wait for refill
# ---------------------------------------------------------

print("\nWaiting for refill...")

time.sleep(2)

print(limiter.stats())

limiter.acquire()

print("Acquire successful after refill.")
print(limiter.stats())

# ---------------------------------------------------------
# Reset
# ---------------------------------------------------------

print("\nResetting limiter...")

limiter.reset()

print(limiter.stats())

print("\nAll tests passed.")