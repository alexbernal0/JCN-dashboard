"""
Enhanced multi-layer caching system with disk persistence
100% free - no Redis required!

Architecture:
- Layer 1: In-memory cache (fast, volatile)
- Layer 2: Disk cache (persistent, survives restarts)
- Layer 3: Smart TTL management (daily for fundamentals, 5min for prices)
"""

import time
import json
import os
import pickle
from typing import Any, Optional
from functools import wraps
from pathlib import Path
from datetime import datetime

class EnhancedCache:
    """Multi-layer cache with memory + disk persistence"""
    
    def __init__(self, disk_cache_dir: str = "/tmp/jcn_cache"):
        # Layer 1: In-memory cache (fast)
        self._memory_cache = {}
        
        # Layer 2: Disk cache (persistent)
        self.disk_cache_dir = Path(disk_cache_dir)
        self.disk_cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Load disk cache into memory on startup
        self._load_disk_cache()
    
    def _load_disk_cache(self):
        """Load disk cache into memory on startup"""
        try:
            cache_file = self.disk_cache_dir / "cache.json"
            if cache_file.exists():
                with open(cache_file, 'r') as f:
                    disk_data = json.load(f)
                    current_time = time.time()
                    # Only load non-expired entries
                    for key, (value, expiry) in disk_data.items():
                        if current_time < expiry:
                            self._memory_cache[key] = (value, expiry)
                print(f"Loaded {len(self._memory_cache)} cached entries from disk")
        except Exception as e:
            print(f"Could not load disk cache: {e}")
    
    def _save_to_disk(self):
        """Persist memory cache to disk"""
        try:
            cache_file = self.disk_cache_dir / "cache.json"
            # Only save non-expired entries
            current_time = time.time()
            valid_entries = {
                k: v for k, v in self._memory_cache.items() 
                if v[1] > current_time
            }
            with open(cache_file, 'w') as f:
                json.dump(valid_entries, f)
        except Exception as e:
            print(f"Could not save to disk cache: {e}")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache (memory first, then disk)"""
        if key in self._memory_cache:
            value, expiry = self._memory_cache[key]
            if time.time() < expiry:
                return value
            else:
                # Expired, remove from cache
                del self._memory_cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: int = 300, persist: bool = True):
        """
        Set value in cache with TTL (seconds)
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            persist: Whether to persist to disk (default True for long TTL)
        """
        expiry = time.time() + ttl
        self._memory_cache[key] = (value, expiry)
        
        # Persist to disk for long-lived cache entries
        if persist and ttl > 300:  # Only persist if TTL > 5 minutes
            self._save_to_disk()
    
    def delete(self, key: str):
        """Delete key from cache"""
        if key in self._memory_cache:
            del self._memory_cache[key]
            self._save_to_disk()
    
    def clear(self):
        """Clear all cache"""
        self._memory_cache.clear()
        try:
            cache_file = self.disk_cache_dir / "cache.json"
            if cache_file.exists():
                cache_file.unlink()
        except Exception as e:
            print(f"Could not clear disk cache: {e}")
    
    def size(self) -> int:
        """Get cache size"""
        # Remove expired entries first
        current_time = time.time()
        expired_keys = [k for k, (_, exp) in self._memory_cache.items() if current_time >= exp]
        for key in expired_keys:
            del self._memory_cache[key]
        return len(self._memory_cache)
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        current_time = time.time()
        total_entries = len(self._memory_cache)
        expired = sum(1 for _, (_, exp) in self._memory_cache.items() if current_time >= exp)
        valid = total_entries - expired
        
        return {
            "total_entries": total_entries,
            "valid_entries": valid,
            "expired_entries": expired,
            "disk_cache_dir": str(self.disk_cache_dir),
            "last_updated": datetime.now().isoformat()
        }

# Global cache instance
cache = EnhancedCache()

def cached(ttl: int = 300, key_prefix: str = "", persist: bool = True):
    """
    Decorator for caching function results
    
    Args:
        ttl: Time to live in seconds
            - 86400 (24h) for MotherDuck fundamentals
            - 300 (5min) for yfinance prices
            - 600 (10min) for portfolio summaries
        key_prefix: Prefix for cache key
        persist: Whether to persist to disk (auto-enabled for TTL > 5min)
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                print(f"Cache HIT: {cache_key[:100]}")
                return cached_value
            
            # Call function and cache result
            print(f"Cache MISS: {cache_key[:100]}")
            result = await func(*args, **kwargs)
            cache.set(cache_key, result, ttl, persist=persist and ttl > 300)
            return result
        
        return wrapper
    return decorator
