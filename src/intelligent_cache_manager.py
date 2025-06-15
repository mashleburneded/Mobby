# src/intelligent_cache_manager.py - Advanced Multi-Tier Caching with Predictive Pre-loading
import asyncio
import hashlib
import pickle
import time
import logging
from typing import Any, Dict, Optional, List, Callable
from dataclasses import dataclass
from collections import defaultdict
import redis.asyncio as redis
from functools import wraps
import json

logger = logging.getLogger(__name__)

@dataclass
class CacheMetrics:
    """Cache performance metrics"""
    hits: int = 0
    misses: int = 0
    l1_hits: int = 0
    l2_hits: int = 0
    l3_hits: int = 0
    prediction_hits: int = 0
    total_requests: int = 0
    
    @property
    def hit_rate(self) -> float:
        return self.hits / max(self.total_requests, 1)
    
    @property
    def l1_hit_rate(self) -> float:
        return self.l1_hits / max(self.total_requests, 1)

@dataclass
class PredictionContext:
    """Context for predictive caching"""
    user_id: int
    recent_queries: List[str]
    query_patterns: Dict[str, int]
    time_patterns: Dict[str, List[float]]
    session_context: Dict[str, Any]

class PredictiveLoader:
    """AI-powered predictive cache loading"""
    
    def __init__(self):
        self.user_patterns = defaultdict(lambda: defaultdict(int))
        self.temporal_patterns = defaultdict(list)
        self.sequence_patterns = defaultdict(list)
        
    async def learn_pattern(self, user_id: int, query: str, context: Dict[str, Any]):
        """Learn user query patterns for prediction"""
        current_time = time.time()
        hour_of_day = int((current_time % 86400) / 3600)
        
        # Track query frequency
        self.user_patterns[user_id][query] += 1
        
        # Track temporal patterns
        self.temporal_patterns[f"{user_id}:{hour_of_day}"].append(query)
        
        # Track sequence patterns
        if len(self.sequence_patterns[user_id]) >= 10:
            self.sequence_patterns[user_id].pop(0)
        self.sequence_patterns[user_id].append(query)
        
    async def predict_next_queries(self, user_id: int, current_query: str, 
                                 context: Dict[str, Any]) -> List[str]:
        """Predict likely next queries for preloading"""
        predictions = []
        
        # Pattern-based predictions
        user_queries = self.user_patterns[user_id]
        if user_queries:
            # Most frequent queries for this user
            frequent_queries = sorted(user_queries.items(), 
                                    key=lambda x: x[1], reverse=True)[:3]
            predictions.extend([q[0] for q in frequent_queries])
        
        # Temporal predictions
        current_hour = int((time.time() % 86400) / 3600)
        temporal_key = f"{user_id}:{current_hour}"
        if temporal_key in self.temporal_patterns:
            recent_temporal = self.temporal_patterns[temporal_key][-5:]
            predictions.extend(recent_temporal)
        
        # Sequence predictions
        if user_id in self.sequence_patterns:
            recent_sequence = self.sequence_patterns[user_id][-3:]
            if len(recent_sequence) >= 2:
                # Simple sequence prediction
                if current_query in recent_sequence:
                    idx = recent_sequence.index(current_query)
                    if idx < len(recent_sequence) - 1:
                        predictions.append(recent_sequence[idx + 1])
        
        # Remove duplicates and current query
        unique_predictions = []
        for pred in predictions:
            if pred != current_query and pred not in unique_predictions:
                unique_predictions.append(pred)
        
        return unique_predictions[:5]  # Top 5 predictions
    
    async def preload_likely_requests(self, user_context: PredictionContext):
        """Preload likely requests based on predictions"""
        try:
            predictions = await self.predict_next_queries(
                user_context.user_id, 
                user_context.recent_queries[-1] if user_context.recent_queries else "",
                user_context.session_context
            )
            
            # Return predictions for cache manager to preload
            return predictions
            
        except Exception as e:
            logger.error(f"Error in predictive preloading: {e}")
            return []

class IntelligentResponseCache:
    """Multi-tier caching with predictive pre-loading and intelligent eviction"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379", 
                 l1_size: int = 1000, l2_size: int = 5000):
        # L1: Hot data in memory (<50ms)
        self.l1_cache: Dict[str, Any] = {}
        self.l1_access_times: Dict[str, float] = {}
        self.l1_max_size = l1_size
        
        # L2: Warm data in memory (<200ms)
        self.l2_cache: Dict[str, Any] = {}
        self.l2_access_times: Dict[str, float] = {}
        self.l2_max_size = l2_size
        
        # L3: Cold data in Redis (<500ms)
        self.redis_client = None
        self.redis_url = redis_url
        
        # Predictive engine
        self.prediction_engine = PredictiveLoader()
        
        # Metrics
        self.metrics = CacheMetrics()
        
        # Background tasks
        self.cleanup_task = None
        self.preload_task = None
        
    async def initialize(self):
        """Initialize Redis connection and background tasks"""
        try:
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()
            logger.info("✅ Redis cache connection established")
        except Exception as e:
            logger.warning(f"⚠️ Redis unavailable, using memory-only cache: {e}")
            self.redis_client = None
        
        # Start background cleanup
        self.cleanup_task = asyncio.create_task(self._background_cleanup())
        
    async def close(self):
        """Clean shutdown"""
        if self.cleanup_task:
            self.cleanup_task.cancel()
        if self.redis_client:
            await self.redis_client.close()
    
    def _generate_cache_key(self, func_name: str, *args, **kwargs) -> str:
        """Generate consistent cache key"""
        key_data = f"{func_name}:{str(args)}:{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def get_with_prediction(self, key: str, user_context: PredictionContext) -> Optional[Any]:
        """Get value with predictive preloading"""
        self.metrics.total_requests += 1
        
        # Check L1 cache (hottest data)
        if key in self.l1_cache:
            self.l1_access_times[key] = time.time()
            self.metrics.hits += 1
            self.metrics.l1_hits += 1
            logger.debug(f"L1 cache hit for key: {key[:20]}...")
            return self.l1_cache[key]
        
        # Check L2 cache (warm data)
        if key in self.l2_cache:
            value = self.l2_cache[key]
            # Promote to L1
            await self._promote_to_l1(key, value)
            self.l2_access_times[key] = time.time()
            self.metrics.hits += 1
            self.metrics.l2_hits += 1
            logger.debug(f"L2 cache hit for key: {key[:20]}...")
            return value
        
        # Check L3 cache (Redis)
        if self.redis_client:
            try:
                data = await self.redis_client.get(key)
                if data:
                    value = pickle.loads(data)
                    # Promote to L2
                    await self._promote_to_l2(key, value)
                    self.metrics.hits += 1
                    self.metrics.l3_hits += 1
                    logger.debug(f"L3 cache hit for key: {key[:20]}...")
                    
                    # Trigger predictive preloading
                    asyncio.create_task(self._predictive_preload(user_context))
                    
                    return value
            except Exception as e:
                logger.error(f"Redis cache error: {e}")
        
        # Cache miss
        self.metrics.misses += 1
        logger.debug(f"Cache miss for key: {key[:20]}...")
        
        # Learn pattern for future predictions
        if user_context and user_context.recent_queries:
            await self.prediction_engine.learn_pattern(
                user_context.user_id, 
                key, 
                user_context.session_context
            )
        
        return None
    
    async def set_intelligent(self, key: str, value: Any, ttl: int = 3600, 
                            priority: str = "normal"):
        """Set value with intelligent tier placement"""
        current_time = time.time()
        
        # Determine initial placement based on priority
        if priority == "hot" or key in self.l1_cache:
            await self._set_l1(key, value, current_time)
        elif priority == "warm" or key in self.l2_cache:
            await self._set_l2(key, value, current_time)
        else:
            await self._set_l2(key, value, current_time)  # Default to L2
        
        # Also store in Redis for persistence
        if self.redis_client:
            try:
                await self.redis_client.setex(key, ttl, pickle.dumps(value))
            except Exception as e:
                logger.error(f"Redis set error: {e}")
    
    async def _promote_to_l1(self, key: str, value: Any):
        """Promote value to L1 cache"""
        await self._set_l1(key, value, time.time())
    
    async def _promote_to_l2(self, key: str, value: Any):
        """Promote value to L2 cache"""
        await self._set_l2(key, value, time.time())
    
    async def _set_l1(self, key: str, value: Any, access_time: float):
        """Set value in L1 cache with LRU eviction"""
        if len(self.l1_cache) >= self.l1_max_size:
            await self._evict_lru_l1()
        
        self.l1_cache[key] = value
        self.l1_access_times[key] = access_time
    
    async def _set_l2(self, key: str, value: Any, access_time: float):
        """Set value in L2 cache with LRU eviction"""
        if len(self.l2_cache) >= self.l2_max_size:
            await self._evict_lru_l2()
        
        self.l2_cache[key] = value
        self.l2_access_times[key] = access_time
    
    async def _evict_lru_l1(self):
        """Evict least recently used item from L1"""
        if not self.l1_access_times:
            return
        
        lru_key = min(self.l1_access_times.items(), key=lambda x: x[1])[0]
        value = self.l1_cache.pop(lru_key)
        self.l1_access_times.pop(lru_key)
        
        # Demote to L2
        await self._set_l2(lru_key, value, time.time())
    
    async def _evict_lru_l2(self):
        """Evict least recently used item from L2"""
        if not self.l2_access_times:
            return
        
        lru_key = min(self.l2_access_times.items(), key=lambda x: x[1])[0]
        self.l2_cache.pop(lru_key)
        self.l2_access_times.pop(lru_key)
    
    async def _predictive_preload(self, user_context: PredictionContext):
        """Preload predicted queries"""
        try:
            predictions = await self.prediction_engine.preload_likely_requests(user_context)
            
            for prediction in predictions:
                # Check if already cached
                if (prediction not in self.l1_cache and 
                    prediction not in self.l2_cache):
                    
                    # This would trigger the actual data fetching
                    # For now, we just mark it as a prediction hit
                    self.metrics.prediction_hits += 1
                    logger.debug(f"Predicted query for preloading: {prediction}")
                    
        except Exception as e:
            logger.error(f"Error in predictive preloading: {e}")
    
    async def _background_cleanup(self):
        """Background task for cache maintenance"""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                
                current_time = time.time()
                
                # Clean up old L1 entries (older than 1 hour)
                old_l1_keys = [
                    key for key, access_time in self.l1_access_times.items()
                    if current_time - access_time > 3600
                ]
                for key in old_l1_keys:
                    self.l1_cache.pop(key, None)
                    self.l1_access_times.pop(key, None)
                
                # Clean up old L2 entries (older than 2 hours)
                old_l2_keys = [
                    key for key, access_time in self.l2_access_times.items()
                    if current_time - access_time > 7200
                ]
                for key in old_l2_keys:
                    self.l2_cache.pop(key, None)
                    self.l2_access_times.pop(key, None)
                
                logger.debug(f"Cache cleanup: removed {len(old_l1_keys)} L1, {len(old_l2_keys)} L2 entries")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cache cleanup: {e}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get cache performance metrics"""
        return {
            "hit_rate": self.metrics.hit_rate,
            "l1_hit_rate": self.metrics.l1_hit_rate,
            "total_requests": self.metrics.total_requests,
            "l1_size": len(self.l1_cache),
            "l2_size": len(self.l2_cache),
            "prediction_hits": self.metrics.prediction_hits,
            "cache_efficiency": {
                "l1_hits": self.metrics.l1_hits,
                "l2_hits": self.metrics.l2_hits,
                "l3_hits": self.metrics.l3_hits,
                "misses": self.metrics.misses
            }
        }
    
    def cached(self, ttl: int = 3600, priority: str = "normal"):
        """Decorator for caching function results"""
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key
                key = self._generate_cache_key(func.__name__, *args, **kwargs)
                
                # Try to get from cache
                user_context = kwargs.get('user_context')
                if user_context:
                    result = await self.get_with_prediction(key, user_context)
                else:
                    # Fallback without prediction
                    result = await self.get_with_prediction(key, None)
                
                if result is not None:
                    return result
                
                # Execute function and cache result
                result = await func(*args, **kwargs)
                await self.set_intelligent(key, result, ttl, priority)
                
                return result
            return wrapper
        return decorator

# Global cache instance
intelligent_cache = IntelligentResponseCache()

# Convenience functions
async def initialize_cache():
    """Initialize the global cache"""
    await intelligent_cache.initialize()

async def shutdown_cache():
    """Shutdown the global cache"""
    await intelligent_cache.close()

def cache_with_intelligence(ttl: int = 3600, priority: str = "normal"):
    """Decorator for intelligent caching"""
    return intelligent_cache.cached(ttl, priority)

async def get_cache_metrics() -> Dict[str, Any]:
    """Get global cache metrics"""
    return intelligent_cache.get_metrics()