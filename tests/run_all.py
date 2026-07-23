"""
============================================================
NPAT - Run All Tests
============================================================
"""

from __future__ import annotations

import subprocess
import sys


TESTS = [
    "tests.test_cache",
    "tests.test_telemetry",
    "tests.test_health",
    "tests.test_circuit_breaker",
    "tests.test_rate_limiter",
]


def run_test(module: str) -> bool:

    print("\n" + "=" * 60)
    print(f"Running {module}")
    print("=" * 60)

    result = subprocess.run(
        [sys.executable, "-m", module]
    )

    return result.returncode == 0


def main() -> None:

    print("=" * 60)
    print("NPAT TEST SUITE")
    print("=" * 60)

    passed = 0

    for module in TESTS:

        if run_test(module):

            passed += 1

    print("\n" + "=" * 60)

    print(
        f"Passed: {passed}/{len(TESTS)}"
    )

    if passed == len(TESTS):

        print("ALL TESTS PASSED")

    else:

        print("SOME TESTS FAILED")

    print("=" * 60)


if __name__ == "__main__":

    main()