"""
=========================================================
NPAT - Cache Manager
=========================================================

Purpose
-------
Central in-memory cache used across NPAT.

Features
--------
✓ Thread Safe
✓ TTL Support
✓ Automatic Expiry
✓ Statistics
✓ Manual Flush
✓ Future Redis Compatible

Author:
Rocky Chopra

Version:
1.0.0
=========================================================
"""

from __future__ import annotations

import time
import threading

from dataclasses import dataclass
from typing import Any, Dict, Optional


# =========================================================
# Cache Entry
# =========================================================

@dataclass(slots=True)
class CacheEntry:

    value: Any

    expiry: float


# =========================================================
# Cache Manager
# =========================================================

class CacheManager:

    def __init__(self):

        self._cache: Dict[str, CacheEntry] = {}

        self._lock = threading.RLock()

        self._hits = 0

        self._misses = 0

    # -----------------------------------------------------

    def set(

        self,

        key: str,

        value: Any,

        ttl: int = 60,

    ) -> None:

        expiry = time.time() + ttl

        with self._lock:

            self._cache[key] = CacheEntry(

                value=value,

                expiry=expiry,

            )

    # -----------------------------------------------------

    def get(

        self,

        key: str,

        default: Optional[Any] = None,

    ) -> Any:

        with self._lock:

            entry = self._cache.get(key)

            if entry is None:

                self._misses += 1

                return default

            if time.time() > entry.expiry:

                del self._cache[key]

                self._misses += 1

                return default

            self._hits += 1

            return entry.value

    # -----------------------------------------------------

    def exists(

        self,

        key: str,

    ) -> bool:

        return self.get(key) is not None

    # -----------------------------------------------------

    def delete(

        self,

        key: str,

    ) -> bool:

        with self._lock:

            return self._cache.pop(key, None) is not None

    # -----------------------------------------------------

    def clear(self) -> None:

        with self._lock:

            self._cache.clear()

    # -----------------------------------------------------

    def cleanup(self) -> int:

        """
        Remove expired entries.

        Returns
        -------
        Number of deleted items.
        """

        removed = 0

        now = time.time()

        with self._lock:

            expired = [

                key

                for key, value in self._cache.items()

                if value.expiry < now

            ]

            for key in expired:

                del self._cache[key]

                removed += 1

        return removed

    # -----------------------------------------------------

    def size(self) -> int:

        with self._lock:

            return len(self._cache)

    # -----------------------------------------------------

    @property

    def hits(self) -> int:

        return self._hits

    # -----------------------------------------------------

    @property

    def misses(self) -> int:

        return self._misses

    # -----------------------------------------------------

    @property

    def hit_rate(self) -> float:

        total = self._hits + self._misses

        if total == 0:

            return 0.0

        return round((self._hits / total) * 100, 2)

    # -----------------------------------------------------

    def stats(self) -> Dict[str, Any]:

        return {

            "entries": self.size(),

            "hits": self._hits,

            "misses": self._misses,

            "hit_rate": self.hit_rate,

        }


# =========================================================
# Global Cache Instance
# =========================================================

cache = CacheManager()