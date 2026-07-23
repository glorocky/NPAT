import time

from services.telemetry import telemetry

print("=" * 60)
print("NPAT TELEMETRY TEST")
print("=" * 60)

with telemetry.track():
    time.sleep(0.5)

with telemetry.track():
    time.sleep(0.2)

try:
    with telemetry.track():
        raise ValueError("Test Error")
except ValueError:
    pass

print()

for key, value in telemetry.stats().items():
    print(f"{key:22}: {value}")