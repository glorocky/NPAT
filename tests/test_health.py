from pprint import pprint

from services.health import health

print("=" * 60)
print("NPAT HEALTH TEST")
print("=" * 60)

health.register("NSE")
health.register("Groww")
health.register("Yahoo")

health.set_healthy("NSE", response_time=0.21)

health.set_warning(
    "Groww",
    "Slow response",
    response_time=2.4,
)

health.set_unhealthy(
    "Yahoo",
    "Timeout",
)

print()

pprint(health.summary())

print()

for name in ("NSE", "Groww", "Yahoo"):

    pprint(health.get(name))