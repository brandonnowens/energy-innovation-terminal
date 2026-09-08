"""High-performance, thread-safe bounded in-memory TTL cache utility."""

import time
import threading
from typing import Any, Optional, Dict, Tuple
from collections import OrderedDict


class TTLCache:
    """Thread-safe, bounded in-memory cache with time-to-live (TTL) and LRU eviction."""

    def __init__(self, ttl_seconds: float = 300.0, max_size: int = 1000):
        self.ttl = ttl_seconds
        self.max_size = max_size
        self._cache: OrderedDict[str, Tuple[float, Any]] = OrderedDict()
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        """Retrieve cached item if it exists and has not expired."""
        with self._lock:
            if key not in self._cache:
                return None
            ts, val = self._cache[key]
            if time.time() - ts > self.ttl:
                del self._cache[key]
                return None
            # Move to end for LRU
            self._cache.move_to_end(key)
            return val

    def set(self, key: str, value: Any) -> Any:
        """Set cached item with current timestamp, evicting oldest if max_size is exceeded."""
        with self._lock:
            now = time.time()
            # If exists, update
            if key in self._cache:
                self._cache[key] = (now, value)
                self._cache.move_to_end(key)
                return value

            # If capacity reached, remove oldest expired first, otherwise pop item
            if len(self._cache) >= self.max_size:
                # Check for expired items to prune
                expired_keys = [k for k, (t, _) in self._cache.items() if now - t > self.ttl]
                if expired_keys:
                    for k in expired_keys:
                        del self._cache[k]
                if len(self._cache) >= self.max_size:
                    self._cache.popitem(last=False)

            self._cache[key] = (now, value)
            return value

    def invalidate(self, key_prefix: Optional[str] = None):
        """Clear cache or all entries matching a prefix."""
        with self._lock:
            if key_prefix:
                keys_to_del = [k for k in self._cache if k.startswith(key_prefix)]
                for k in keys_to_del:
                    del self._cache[k]
            else:
                self._cache.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._cache)
