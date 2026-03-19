from __future__ import annotations

import time
from typing import Any, Dict, Optional


class TTLCache:
    def __init__(self, ttl_seconds: int) -> None:
        self._ttl = ttl_seconds
        self._store: Dict[str, Dict[str, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        entry = self._store.get(key)
        if not entry:
            return None
        if time.time() - entry["ts"] > self._ttl:
            self._store.pop(key, None)
            return None
        return entry["value"]

    def set(self, key: str, value: Any) -> None:
        self._store[key] = {"value": value, "ts": time.time()}

    def invalidate(self, key: str) -> None:
        self._store.pop(key, None)

    def invalidate_all(self) -> None:
        self._store.clear()
