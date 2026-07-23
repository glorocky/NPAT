import time

from services.circuit_breaker import (
    CircuitBreaker,
    CircuitState,
)
from services.exceptions import CircuitOpenException


def print_state(breaker):
    print(
        f"State={breaker.state.value}, "
        f"Failures={breaker.failure_count}, "
        f"Successes={breaker.success_count}"
    )


print("=" * 60)
print("NPAT CIRCUIT BREAKER TEST")
print("=" * 60)

breaker = CircuitBreaker(
    name="NSE",
    failure_threshold=3,
    recovery_timeout=2,
    success_threshold=2,
)

print("\nInitial")
print_state(breaker)

# Three failures
for i in range(3):
    breaker.record_failure()

print("\nAfter Failures")
print_state(breaker)

assert breaker.state == CircuitState.OPEN

# Should block immediately
try:
    breaker.before_request()
except CircuitOpenException:
    print("\nCircuit correctly blocked request.")

print("\nWaiting for recovery...")

time.sleep(2.2)

breaker.before_request()

print("\nRecovered to HALF_OPEN")
print_state(breaker)

assert breaker.state == CircuitState.HALF_OPEN

breaker.record_success()

print("\nOne Success")
print_state(breaker)

breaker.record_success()

print("\nRecovered")
print_state(breaker)

assert breaker.state == CircuitState.CLOSED

print("\nAll tests passed.")