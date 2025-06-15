#!/usr/bin/env python3
"""
SECURE REDIS CACHE MANAGER
==========================
High-performance Redis caching with security, encryption, and intelligent cache strategies.
"""

import asyncio
import aioredis
import json
import logging
import hashlib
import time
import secrets
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import pickle
import zlib
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

@dataclass
class CacheConfig:
    """Redis cache configuration"""
    host: str = "localhost"
    port: int = 6379
    password: Optional[str] = None
    db: int = 0
    max_connections: int = 20
    connection_timeout: float = 5.0
    socket_timeout: float = 5.0
    retry_on_timeout: bool = True
    health_check_interval: float = 30.0
    enable_encryption: bool = True
    default_ttl: int = 3600  # 1 hour
    max_memory_policy: str = "allkeys-lru"

@dataclass
class CacheStats:
    """Cache statistics"""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    errors: int = 0
    total_requests: int = 0
    avg_response_time: float = 0.0
    memory_usage: int = 0
    connected_clients: int = 0

class SecureRedisCache:
    """High-performance secure Redis cache manager"""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.redis: Optional[aioredis.Redis] = None
        self.connection_pool: Optional[aioredis.ConnectionPool] = None
        self.stats = CacheStats()
        self.encryption_key = self._generate_encryption_key()
        self.circuit_breaker = CircuitBreaker()
        self.rate_limiter = CacheRateLimiter()
        
    def _generate_encryption_key(self) -> bytes:
        """Generate encryption key for cache data"""
        # In production, this should be loaded from secure key management
        return hashlib.sha256(b"mobius_cache_key_v1").digest()
    
    async def initialize(self) -> bool:
        """Initialize Redis connection with security hardening"""
        try:
            logger.info("Initializing secure Redis cache...")
            
            # Create connection pool
            self.connection_pool = aioredis.ConnectionPool(
                host=self.config.host,
                port=self.config.port,
                password=self.config.password,
                db=self.config.db,
                max_connections=self.config.max_connections,
                socket_timeout=self.config.socket_timeout,
                socket_connect_timeout=self.config.connection_timeout,
                retry_on_timeout=self.config.retry_on_timeout,
                health_check_interval=self.config.health_check_interval
            )
            
            # Create Redis client
            self.redis = aioredis.Redis(connection_pool=self.connection_pool)
            
            # Test connection
            await self.redis.ping()
            
            # Configure Redis for security and performance
            await self._configure_redis_security()
            
            logger.info("✅ Secure Redis cache initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis cache: {e}")
            return False
    
    async def _configure_redis_security(self):
        """Configure Redis for security and performance"""
        try:
            # Set memory policy
            await self.redis.config_set("maxmemory-policy", self.config.max_memory_policy)
            
            # Disable dangerous commands (if we have admin access)
            dangerous_commands = ["FLUSHDB", "FLUSHALL", "KEYS", "CONFIG", "SHUTDOWN", "DEBUG"]
            for cmd in dangerous_commands:
                try:
                    await self.redis.config_set(f"rename-command {cmd}", f"{cmd}_DISABLED")
                except:
                    pass  # Ignore if we don't have permission
            
            # Set up key expiration policies
            await self.redis.config_set("notify-keyspace-events", "Ex")  # Enable expiration events
            
        except Exception as e:
            logger.warning(f"Could not configure Redis security settings: {e}")
    
    async def get(self, key: str, user_id: Optional[int] = None) -> Optional[Any]:
        """Get value from cache with security checks"""
        start_time = time.time()
        
        try:
            # Rate limiting
            if user_id and not await self.rate_limiter.check_rate_limit(user_id):
                logger.warning(f"Rate limit exceeded for user {user_id}")
                return None
            
            # Circuit breaker check
            if not self.circuit_breaker.can_execute():
                logger.warning("Circuit breaker is open, skipping cache")
                return None
            
            # Secure key generation
            secure_key = self._generate_secure_key(key, user_id)
            
            # Get from Redis
            cached_data = await self.redis.get(secure_key)
            
            if cached_data:
                # Decrypt and deserialize
                decrypted_data = self._decrypt_data(cached_data)
                result = self._deserialize_data(decrypted_data)
                
                # Update stats
                self.stats.hits += 1
                self.circuit_breaker.record_success()
                
                return result
            else:
                self.stats.misses += 1
                return None
                
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            self.stats.errors += 1
            self.circuit_breaker.record_failure()
            return None
        finally:
            # Update response time stats
            response_time = time.time() - start_time
            self.stats.total_requests += 1
            self.stats.avg_response_time = (
                (self.stats.avg_response_time * (self.stats.total_requests - 1) + response_time)
                / self.stats.total_requests
            )
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None, user_id: Optional[int] = None) -> bool:
        """Set value in cache with security and compression"""
        try:
            # Rate limiting
            if user_id and not await self.rate_limiter.check_rate_limit(user_id):
                logger.warning(f"Rate limit exceeded for user {user_id}")
                return False
            
            # Circuit breaker check
            if not self.circuit_breaker.can_execute():
                logger.warning("Circuit breaker is open, skipping cache")
                return False
            
            # Secure key generation
            secure_key = self._generate_secure_key(key, user_id)
            
            # Serialize and encrypt data
            serialized_data = self._serialize_data(value)
            encrypted_data = self._encrypt_data(serialized_data)
            
            # Set TTL
            cache_ttl = ttl or self.config.default_ttl
            
            # Store in Redis
            await self.redis.setex(secure_key, cache_ttl, encrypted_data)
            
            # Update stats
            self.stats.sets += 1
            self.circuit_breaker.record_success()
            
            return True
            
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            self.stats.errors += 1
            self.circuit_breaker.record_failure()
            return False
    
    async def delete(self, key: str, user_id: Optional[int] = None) -> bool:
        """Delete value from cache"""
        try:
            secure_key = self._generate_secure_key(key, user_id)
            result = await self.redis.delete(secure_key)
            
            if result:
                self.stats.deletes += 1
            
            return bool(result)
            
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            self.stats.errors += 1
            return False
    
    async def exists(self, key: str, user_id: Optional[int] = None) -> bool:
        """Check if key exists in cache"""
        try:
            secure_key = self._generate_secure_key(key, user_id)
            return bool(await self.redis.exists(secure_key))
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False
    
    async def get_or_set(self, key: str, factory: Callable, ttl: Optional[int] = None, 
                        user_id: Optional[int] = None) -> Any:
        """Get value from cache or set it using factory function"""
        # Try to get from cache first
        cached_value = await self.get(key, user_id)
        if cached_value is not None:
            return cached_value
        
        # Generate value using factory
        try:
            if asyncio.iscoroutinefunction(factory):
                value = await factory()
            else:
                value = factory()
            
            # Cache the value
            await self.set(key, value, ttl, user_id)
            return value
            
        except Exception as e:
            logger.error(f"Factory function error for key {key}: {e}")
            return None
    
    async def get_multi(self, keys: List[str], user_id: Optional[int] = None) -> Dict[str, Any]:
        """Get multiple values from cache"""
        results = {}
        
        # Generate secure keys
        secure_keys = [self._generate_secure_key(key, user_id) for key in keys]
        
        try:
            # Get all values at once
            cached_values = await self.redis.mget(secure_keys)
            
            for i, (original_key, cached_data) in enumerate(zip(keys, cached_values)):
                if cached_data:
                    try:
                        decrypted_data = self._decrypt_data(cached_data)
                        results[original_key] = self._deserialize_data(decrypted_data)
                        self.stats.hits += 1
                    except Exception as e:
                        logger.error(f"Error deserializing cached data for key {original_key}: {e}")
                        self.stats.errors += 1
                else:
                    self.stats.misses += 1
            
        except Exception as e:
            logger.error(f"Cache multi-get error: {e}")
            self.stats.errors += 1
        
        return results
    
    async def set_multi(self, data: Dict[str, Any], ttl: Optional[int] = None, 
                       user_id: Optional[int] = None) -> bool:
        """Set multiple values in cache"""
        try:
            pipe = self.redis.pipeline()
            cache_ttl = ttl or self.config.default_ttl
            
            for key, value in data.items():
                secure_key = self._generate_secure_key(key, user_id)
                serialized_data = self._serialize_data(value)
                encrypted_data = self._encrypt_data(serialized_data)
                pipe.setex(secure_key, cache_ttl, encrypted_data)
            
            await pipe.execute()
            self.stats.sets += len(data)
            return True
            
        except Exception as e:
            logger.error(f"Cache multi-set error: {e}")
            self.stats.errors += 1
            return False
    
    def _generate_secure_key(self, key: str, user_id: Optional[int] = None) -> str:
        """Generate secure cache key with namespace and user isolation"""
        # Add namespace
        namespaced_key = f"mobius:cache:{key}"
        
        # Add user isolation if provided
        if user_id:
            namespaced_key = f"mobius:user:{user_id}:cache:{key}"
        
        # Hash long keys to prevent key length issues
        if len(namespaced_key) > 250:  # Redis key limit is 512MB, but keep it reasonable
            key_hash = hashlib.sha256(namespaced_key.encode()).hexdigest()
            namespaced_key = f"mobius:hash:{key_hash}"
        
        return namespaced_key
    
    def _serialize_data(self, data: Any) -> bytes:
        """Serialize data with compression"""
        try:
            # Use pickle for Python objects, with compression
            serialized = pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
            compressed = zlib.compress(serialized, level=6)  # Good balance of speed/compression
            return compressed
        except Exception as e:
            logger.error(f"Serialization error: {e}")
            # Fallback to JSON
            return json.dumps(data).encode()
    
    def _deserialize_data(self, data: bytes) -> Any:
        """Deserialize data with decompression"""
        try:
            # Try pickle with compression first
            decompressed = zlib.decompress(data)
            return pickle.loads(decompressed)
        except:
            try:
                # Fallback to JSON
                return json.loads(data.decode())
            except Exception as e:
                logger.error(f"Deserialization error: {e}")
                return None
    
    def _encrypt_data(self, data: bytes) -> bytes:
        """Encrypt cache data for security"""
        if not self.config.enable_encryption:
            return data
        
        # Simple XOR encryption for demo - use proper encryption in production
        key_bytes = self.encryption_key
        encrypted = bytearray()
        
        for i, byte in enumerate(data):
            encrypted.append(byte ^ key_bytes[i % len(key_bytes)])
        
        return bytes(encrypted)
    
    def _decrypt_data(self, data: bytes) -> bytes:
        """Decrypt cache data"""
        if not self.config.enable_encryption:
            return data
        
        # Simple XOR decryption
        return self._encrypt_data(data)  # XOR is symmetric
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        try:
            # Get Redis info
            redis_info = await self.redis.info()
            
            # Update stats with Redis metrics
            self.stats.memory_usage = redis_info.get('used_memory', 0)
            self.stats.connected_clients = redis_info.get('connected_clients', 0)
            
            return {
                'cache_stats': asdict(self.stats),
                'redis_info': {
                    'version': redis_info.get('redis_version', 'unknown'),
                    'uptime': redis_info.get('uptime_in_seconds', 0),
                    'memory_usage': redis_info.get('used_memory_human', '0B'),
                    'memory_peak': redis_info.get('used_memory_peak_human', '0B'),
                    'connected_clients': redis_info.get('connected_clients', 0),
                    'total_commands_processed': redis_info.get('total_commands_processed', 0),
                    'keyspace_hits': redis_info.get('keyspace_hits', 0),
                    'keyspace_misses': redis_info.get('keyspace_misses', 0)
                },
                'circuit_breaker': {
                    'state': self.circuit_breaker.state,
                    'failure_count': self.circuit_breaker.failure_count,
                    'last_failure_time': self.circuit_breaker.last_failure_time
                },
                'hit_ratio': self.stats.hits / max(self.stats.total_requests, 1),
                'error_ratio': self.stats.errors / max(self.stats.total_requests, 1)
            }
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {'error': str(e)}
    
    async def health_check(self) -> bool:
        """Perform cache health check"""
        try:
            # Test basic operations
            test_key = f"health_check_{int(time.time())}"
            test_value = {"timestamp": time.time(), "test": True}
            
            # Test set
            await self.set(test_key, test_value, ttl=60)
            
            # Test get
            retrieved = await self.get(test_key)
            
            # Test delete
            await self.delete(test_key)
            
            # Verify data integrity
            return retrieved is not None and retrieved.get("test") is True
            
        except Exception as e:
            logger.error(f"Cache health check failed: {e}")
            return False
    
    async def cleanup(self):
        """Clean up Redis connections"""
        try:
            if self.redis:
                await self.redis.close()
            if self.connection_pool:
                await self.connection_pool.disconnect()
            logger.info("✅ Redis cache connections cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up Redis cache: {e}")

class CircuitBreaker:
    """Circuit breaker for cache resilience"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def can_execute(self) -> bool:
        """Check if operation can be executed"""
        if self.state == "CLOSED":
            return True
        elif self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                return True
            return False
        else:  # HALF_OPEN
            return True
    
    def record_success(self):
        """Record successful operation"""
        if self.state == "HALF_OPEN":
            self.state = "CLOSED"
            self.failure_count = 0
    
    def record_failure(self):
        """Record failed operation"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

class CacheRateLimiter:
    """Rate limiter for cache operations"""
    
    def __init__(self, max_requests_per_minute: int = 1000):
        self.max_requests_per_minute = max_requests_per_minute
        self.user_requests: Dict[int, List[float]] = {}
    
    async def check_rate_limit(self, user_id: int) -> bool:
        """Check if user is within rate limits"""
        now = time.time()
        minute_ago = now - 60
        
        # Clean old requests
        if user_id in self.user_requests:
            self.user_requests[user_id] = [
                req_time for req_time in self.user_requests[user_id] 
                if req_time > minute_ago
            ]
        else:
            self.user_requests[user_id] = []
        
        # Check limit
        if len(self.user_requests[user_id]) >= self.max_requests_per_minute:
            return False
        
        # Add current request
        self.user_requests[user_id].append(now)
        return True

# Cache decorators for easy use
def cache_result(ttl: int = 3600, key_prefix: str = ""):
    """Decorator to cache function results"""
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key_parts = [key_prefix, func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
            cache_key = ":".join(filter(None, key_parts))
            
            # Try to get from cache
            cached_result = await secure_cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            await secure_cache.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator

# Global cache instance
cache_config = CacheConfig()
secure_cache = SecureRedisCache(cache_config)

# Convenience functions
async def init_cache() -> bool:
    """Initialize cache system"""
    return await secure_cache.initialize()

async def get_cached(key: str, user_id: Optional[int] = None) -> Optional[Any]:
    """Get value from cache"""
    return await secure_cache.get(key, user_id)

async def set_cached(key: str, value: Any, ttl: Optional[int] = None, user_id: Optional[int] = None) -> bool:
    """Set value in cache"""
    return await secure_cache.set(key, value, ttl, user_id)

async def delete_cached(key: str, user_id: Optional[int] = None) -> bool:
    """Delete value from cache"""
    return await secure_cache.delete(key, user_id)

async def cache_health_check() -> bool:
    """Perform cache health check"""
    return await secure_cache.health_check()