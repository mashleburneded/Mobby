# src/intelligent_cache.py
"""
Intelligent Caching System with TTL and Smart Invalidation
Optimizes performance by caching frequently accessed data
"""

import asyncio
import time
import json
import hashlib
from typing import Any, Dict, Optional, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class CacheType(Enum):
    """Types of cached data with different TTL strategies"""
    PRICE = "price"              # 1 minute TTL
    MARKET_DATA = "market_data"  # 5 minutes TTL
    ANALYSIS = "analysis"        # 1 hour TTL
    USER_CONTEXT = "user_context" # 24 hours TTL
    PORTFOLIO = "portfolio"      # 10 minutes TTL
    NEWS = "news"               # 30 minutes TTL
    YIELD_DATA = "yield_data"   # 15 minutes TTL

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    data: Any
    timestamp: float
    ttl: int
    access_count: int = 0
    last_access: float = 0
    cache_type: CacheType = CacheType.ANALYSIS
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        return time.time() - self.timestamp > self.ttl
    
    def access(self) -> Any:
        """Access cached data and update metadata"""
        self.access_count += 1
        self.last_access = time.time()
        return self.data

class IntelligentCache:
    """Intelligent caching system with TTL and smart invalidation"""
    
    def __init__(self, max_size: int = 10000):
        self.cache: Dict[str, CacheEntry] = {}
        self.max_size = max_size
        
        # TTL configurations (in seconds)
        self.ttl_config = {
            CacheType.PRICE: 60,           # 1 minute for prices
            CacheType.MARKET_DATA: 300,    # 5 minutes for market data
            CacheType.ANALYSIS: 3600,      # 1 hour for analysis
            CacheType.USER_CONTEXT: 86400, # 24 hours for user context
            CacheType.PORTFOLIO: 600,      # 10 minutes for portfolio
            CacheType.NEWS: 1800,          # 30 minutes for news
            CacheType.YIELD_DATA: 900,     # 15 minutes for yield data
        }
        
        # Statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'invalidations': 0
        }
        
        # Start cleanup task
        self._cleanup_task = None
        # Don't start cleanup task during init - will be started on first use
    
    def _generate_key(self, prefix: str, **kwargs) -> str:
        """Generate cache key from parameters"""
        # Sort kwargs for consistent key generation
        sorted_kwargs = sorted(kwargs.items())
        key_data = f"{prefix}:{json.dumps(sorted_kwargs, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def get_or_compute(
        self, 
        cache_key: str, 
        compute_func: Callable, 
        cache_type: CacheType,
        force_refresh: bool = False
    ) -> Any:
        """Get cached data or compute and cache it"""
        
        # Start cleanup task if not already running
        if self._cleanup_task is None or self._cleanup_task.done():
            self.start_cleanup_task()
        
        # Check cache first (unless force refresh)
        if not force_refresh and cache_key in self.cache:
            entry = self.cache[cache_key]
            if not entry.is_expired():
                self.stats['hits'] += 1
                logger.debug(f"Cache hit for key: {cache_key[:16]}...")
                return entry.access()
            else:
                # Remove expired entry
                del self.cache[cache_key]
                logger.debug(f"Cache expired for key: {cache_key[:16]}...")
        
        # Cache miss - compute value
        self.stats['misses'] += 1
        logger.debug(f"Cache miss for key: {cache_key[:16]}...")
        
        try:
            # Compute the value
            if asyncio.iscoroutinefunction(compute_func):
                result = await compute_func()
            else:
                result = compute_func()
            
            # Cache the result
            await self._store(cache_key, result, cache_type)
            return result
            
        except Exception as e:
            logger.error(f"Error computing value for cache key {cache_key[:16]}: {e}")
            raise
    
    async def _store(self, key: str, data: Any, cache_type: CacheType):
        """Store data in cache with TTL"""
        ttl = self.ttl_config.get(cache_type, 3600)
        
        entry = CacheEntry(
            data=data,
            timestamp=time.time(),
            ttl=ttl,
            cache_type=cache_type
        )
        
        self.cache[key] = entry
        
        # Evict if cache is too large
        if len(self.cache) > self.max_size:
            await self._evict_lru()
        
        logger.debug(f"Cached data with TTL {ttl}s for key: {key[:16]}...")
    
    async def _evict_lru(self):
        """Evict least recently used entries"""
        if not self.cache:
            return
        
        # Sort by last access time (oldest first)
        sorted_entries = sorted(
            self.cache.items(),
            key=lambda x: x[1].last_access or x[1].timestamp
        )
        
        # Remove oldest 10% of entries
        evict_count = max(1, len(sorted_entries) // 10)
        
        for i in range(evict_count):
            key, _ = sorted_entries[i]
            del self.cache[key]
            self.stats['evictions'] += 1
        
        logger.debug(f"Evicted {evict_count} LRU entries")
    
    async def invalidate_pattern(self, pattern: str):
        """Invalidate all cache entries matching pattern"""
        keys_to_remove = [key for key in self.cache.keys() if pattern in key]
        
        for key in keys_to_remove:
            del self.cache[key]
            self.stats['invalidations'] += 1
        
        logger.debug(f"Invalidated {len(keys_to_remove)} entries matching pattern: {pattern}")
    
    async def invalidate_type(self, cache_type: CacheType):
        """Invalidate all cache entries of specific type"""
        keys_to_remove = [
            key for key, entry in self.cache.items() 
            if entry.cache_type == cache_type
        ]
        
        for key in keys_to_remove:
            del self.cache[key]
            self.stats['invalidations'] += 1
        
        logger.debug(f"Invalidated {len(keys_to_remove)} entries of type: {cache_type.value}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hit_rate': f"{hit_rate:.1f}%",
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'evictions': self.stats['evictions'],
            'invalidations': self.stats['invalidations'],
            'memory_usage': self._estimate_memory_usage()
        }
    
    def _estimate_memory_usage(self) -> str:
        """Estimate memory usage of cache"""
        try:
            import sys
            total_size = sum(sys.getsizeof(entry.data) for entry in self.cache.values())
            
            if total_size < 1024:
                return f"{total_size} B"
            elif total_size < 1024 * 1024:
                return f"{total_size / 1024:.1f} KB"
            else:
                return f"{total_size / (1024 * 1024):.1f} MB"
        except:
            return "Unknown"
    
    async def cleanup_expired(self):
        """Remove expired cache entries"""
        expired_keys = [
            key for key, entry in self.cache.items()
            if entry.is_expired()
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def start_cleanup_task(self):
        """Start background cleanup task"""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def _cleanup_loop(self):
        """Background cleanup loop"""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                await self.cleanup_expired()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cache cleanup loop: {e}")
    
    async def shutdown(self):
        """Shutdown cache and cleanup tasks"""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        self.cache.clear()
        logger.info("Cache shutdown complete")

# Global cache instance
intelligent_cache = IntelligentCache()

# Convenience functions for common cache operations
async def cache_price_data(symbol: str, compute_func: Callable) -> Any:
    """Cache price data with 1-minute TTL"""
    key = intelligent_cache._generate_key("price", symbol=symbol)
    return await intelligent_cache.get_or_compute(key, compute_func, CacheType.PRICE)

async def cache_market_data(symbol: str, compute_func: Callable) -> Any:
    """Cache market data with 5-minute TTL"""
    key = intelligent_cache._generate_key("market", symbol=symbol)
    return await intelligent_cache.get_or_compute(key, compute_func, CacheType.MARKET_DATA)

async def cache_analysis(analysis_type: str, symbol: str, compute_func: Callable) -> Any:
    """Cache analysis data with 1-hour TTL"""
    key = intelligent_cache._generate_key("analysis", type=analysis_type, symbol=symbol)
    return await intelligent_cache.get_or_compute(key, compute_func, CacheType.ANALYSIS)

async def cache_portfolio_data(user_id: int, compute_func: Callable) -> Any:
    """Cache portfolio data with 10-minute TTL"""
    key = intelligent_cache._generate_key("portfolio", user_id=user_id)
    return await intelligent_cache.get_or_compute(key, compute_func, CacheType.PORTFOLIO)

async def cache_yield_data(compute_func: Callable, **filters) -> Any:
    """Cache yield data with 15-minute TTL"""
    key = intelligent_cache._generate_key("yield", **filters)
    return await intelligent_cache.get_or_compute(key, compute_func, CacheType.YIELD_DATA)

async def invalidate_user_cache(user_id: int):
    """Invalidate all cache entries for a specific user"""
    await intelligent_cache.invalidate_pattern(f"user_id={user_id}")

async def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics"""
    return intelligent_cache.get_stats()

async def cleanup_cache():
    """Cleanup cache resources"""
    await intelligent_cache.shutdown()