# src/error_recovery_system.py
"""
Comprehensive Error Recovery and Resilience System
Implements circuit breakers, retry logic, graceful degradation, and alternative data sources
"""

import asyncio
import logging
import json
import time
import random
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque
import aiohttp
import sqlite3

logger = logging.getLogger(__name__)

class ErrorType(Enum):
    """Types of errors for categorization"""
    NETWORK_ERROR = "network_error"
    API_RATE_LIMIT = "api_rate_limit"
    API_QUOTA_EXCEEDED = "api_quota_exceeded"
    API_AUTHENTICATION = "api_authentication"
    API_SERVER_ERROR = "api_server_error"
    DATA_PARSING_ERROR = "data_parsing_error"
    TIMEOUT_ERROR = "timeout_error"
    UNKNOWN_ERROR = "unknown_error"

class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, don't try
    HALF_OPEN = "half_open"  # Testing if service recovered

class RetryStrategy(Enum):
    """Retry strategies"""
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_DELAY = "fixed_delay"
    IMMEDIATE = "immediate"
    NO_RETRY = "no_retry"

@dataclass
class ErrorRecord:
    """Record of an error occurrence"""
    error_id: str
    service_name: str
    error_type: ErrorType
    error_message: str
    timestamp: datetime
    context: Dict[str, Any]
    retry_count: int
    resolved: bool
    resolution_time: Optional[datetime]

@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker"""
    failure_threshold: int = 5
    recovery_timeout: int = 60  # seconds
    success_threshold: int = 3  # successes needed to close from half-open
    timeout: float = 30.0  # request timeout

@dataclass
class RetryConfig:
    """Configuration for retry logic"""
    max_retries: int = 3
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    base_delay: float = 1.0
    max_delay: float = 60.0
    jitter: bool = True

@dataclass
class ServiceHealth:
    """Health status of a service"""
    service_name: str
    is_healthy: bool
    last_success: Optional[datetime]
    last_failure: Optional[datetime]
    consecutive_failures: int
    consecutive_successes: int
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    circuit_breaker_state: CircuitBreakerState

class ErrorRecoverySystem:
    """Comprehensive error recovery and resilience system"""
    
    def __init__(self, db_path: str = "data/error_recovery.db"):
        self.db_path = db_path
        self.circuit_breakers = {}
        self.service_health = {}
        self.error_history = deque(maxlen=1000)
        self.alternative_sources = {}
        self.cached_responses = {}
        self.cache_ttl = {}
        self._initialize_database()
        self._initialize_services()
    
    def _initialize_database(self):
        """Initialize SQLite database for error tracking"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS error_records (
                    error_id TEXT PRIMARY KEY,
                    service_name TEXT,
                    error_type TEXT,
                    error_message TEXT,
                    timestamp TEXT,
                    context TEXT,
                    retry_count INTEGER,
                    resolved BOOLEAN,
                    resolution_time TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS service_health (
                    service_name TEXT PRIMARY KEY,
                    is_healthy BOOLEAN,
                    last_success TEXT,
                    last_failure TEXT,
                    consecutive_failures INTEGER,
                    consecutive_successes INTEGER,
                    total_requests INTEGER,
                    successful_requests INTEGER,
                    failed_requests INTEGER,
                    avg_response_time REAL,
                    circuit_breaker_state TEXT
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_error_service ON error_records(service_name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_error_timestamp ON error_records(timestamp)")
    
    def _initialize_services(self):
        """Initialize service configurations"""
        services = {
            "coingecko": {
                "circuit_breaker": CircuitBreakerConfig(failure_threshold=3, recovery_timeout=30),
                "retry": RetryConfig(max_retries=2, strategy=RetryStrategy.EXPONENTIAL_BACKOFF),
                "alternatives": ["coinmarketcap", "binance_api"],
                "cache_ttl": 300  # 5 minutes
            },
            "defillama": {
                "circuit_breaker": CircuitBreakerConfig(failure_threshold=3, recovery_timeout=60),
                "retry": RetryConfig(max_retries=3, strategy=RetryStrategy.EXPONENTIAL_BACKOFF),
                "alternatives": ["defi_pulse", "apy_vision"],
                "cache_ttl": 600  # 10 minutes
            },
            "groq": {
                "circuit_breaker": CircuitBreakerConfig(failure_threshold=5, recovery_timeout=30),
                "retry": RetryConfig(max_retries=1, strategy=RetryStrategy.IMMEDIATE),
                "alternatives": ["openai", "gemini"],
                "cache_ttl": 0  # No caching for AI responses
            },
            "openai": {
                "circuit_breaker": CircuitBreakerConfig(failure_threshold=3, recovery_timeout=60),
                "retry": RetryConfig(max_retries=2, strategy=RetryStrategy.LINEAR_BACKOFF),
                "alternatives": ["gemini", "anthropic"],
                "cache_ttl": 0
            },
            "gemini": {
                "circuit_breaker": CircuitBreakerConfig(failure_threshold=3, recovery_timeout=45),
                "retry": RetryConfig(max_retries=2, strategy=RetryStrategy.EXPONENTIAL_BACKOFF),
                "alternatives": ["openai", "groq"],
                "cache_ttl": 0
            },
            "news_api": {
                "circuit_breaker": CircuitBreakerConfig(failure_threshold=5, recovery_timeout=120),
                "retry": RetryConfig(max_retries=3, strategy=RetryStrategy.EXPONENTIAL_BACKOFF),
                "alternatives": ["crypto_news_api", "reddit_api"],
                "cache_ttl": 1800  # 30 minutes
            }
        }
        
        for service_name, config in services.items():
            self.circuit_breakers[service_name] = {
                "state": CircuitBreakerState.CLOSED,
                "failure_count": 0,
                "success_count": 0,
                "last_failure_time": None,
                "config": config["circuit_breaker"]
            }
            
            self.service_health[service_name] = ServiceHealth(
                service_name=service_name,
                is_healthy=True,
                last_success=None,
                last_failure=None,
                consecutive_failures=0,
                consecutive_successes=0,
                total_requests=0,
                successful_requests=0,
                failed_requests=0,
                avg_response_time=0.0,
                circuit_breaker_state=CircuitBreakerState.CLOSED
            )
            
            self.alternative_sources[service_name] = config["alternatives"]
            self.cache_ttl[service_name] = config["cache_ttl"]
    
    async def execute_with_recovery(self, 
                                  service_name: str, 
                                  operation: Callable, 
                                  *args, 
                                  **kwargs) -> Dict[str, Any]:
        """Execute operation with comprehensive error recovery"""
        
        # Check circuit breaker
        if not self._is_circuit_closed(service_name):
            logger.warning(f"Circuit breaker open for {service_name}, trying alternatives")
            return await self._try_alternatives(service_name, operation, *args, **kwargs)
        
        # Check cache first
        cache_key = self._generate_cache_key(service_name, args, kwargs)
        cached_result = self._get_cached_response(service_name, cache_key)
        if cached_result:
            logger.info(f"Returning cached response for {service_name}")
            return cached_result
        
        # Execute with retry logic
        retry_config = self._get_retry_config(service_name)
        
        for attempt in range(retry_config.max_retries + 1):
            try:
                start_time = time.time()
                
                # Execute the operation
                result = await self._execute_operation(operation, *args, **kwargs)
                
                # Record success
                response_time = time.time() - start_time
                await self._record_success(service_name, response_time)
                
                # Cache the result if applicable
                if self.cache_ttl[service_name] > 0:
                    self._cache_response(service_name, cache_key, result)
                
                return {
                    "type": "success",
                    "data": result,
                    "service": service_name,
                    "attempt": attempt + 1,
                    "response_time": response_time
                }
                
            except Exception as e:
                error_type = self._classify_error(e)
                
                # Record the error
                await self._record_error(service_name, error_type, str(e), attempt, {
                    "args": str(args),
                    "kwargs": str(kwargs)
                })
                
                # Check if we should retry
                if attempt < retry_config.max_retries and self._should_retry(error_type):
                    delay = self._calculate_retry_delay(retry_config, attempt)
                    logger.warning(f"Attempt {attempt + 1} failed for {service_name}, retrying in {delay}s: {e}")
                    await asyncio.sleep(delay)
                    continue
                else:
                    # All retries exhausted, try alternatives
                    logger.error(f"All retries exhausted for {service_name}: {e}")
                    return await self._try_alternatives(service_name, operation, *args, **kwargs)
        
        # This should never be reached, but just in case
        return {
            "type": "error",
            "message": f"Service {service_name} is unavailable",
            "service": service_name
        }
    
    async def _execute_operation(self, operation: Callable, *args, **kwargs) -> Any:
        """Execute the operation with timeout"""
        try:
            # Check if operation accepts timeout parameter
            import inspect
            sig = inspect.signature(operation)
            
            # Only add timeout if the function accepts it
            if 'timeout' in sig.parameters and 'timeout' not in kwargs:
                kwargs['timeout'] = 30.0
            
            # Execute with timeout wrapper if operation doesn't support timeout
            if 'timeout' not in sig.parameters:
                return await asyncio.wait_for(operation(*args, **kwargs), timeout=30.0)
            else:
                return await operation(*args, **kwargs)
                
        except asyncio.TimeoutError:
            raise TimeoutError("Operation timed out")
    
    def _classify_error(self, error: Exception) -> ErrorType:
        """Classify error type for appropriate handling"""
        error_str = str(error).lower()
        
        if "timeout" in error_str or isinstance(error, (asyncio.TimeoutError, TimeoutError)):
            return ErrorType.TIMEOUT_ERROR
        elif "rate limit" in error_str or "429" in error_str:
            return ErrorType.API_RATE_LIMIT
        elif "quota" in error_str or "exceeded" in error_str:
            return ErrorType.API_QUOTA_EXCEEDED
        elif "unauthorized" in error_str or "401" in error_str or "403" in error_str:
            return ErrorType.API_AUTHENTICATION
        elif "500" in error_str or "502" in error_str or "503" in error_str or "504" in error_str:
            return ErrorType.API_SERVER_ERROR
        elif "connection" in error_str or "network" in error_str:
            return ErrorType.NETWORK_ERROR
        elif "json" in error_str or "parse" in error_str:
            return ErrorType.DATA_PARSING_ERROR
        else:
            return ErrorType.UNKNOWN_ERROR
    
    def _should_retry(self, error_type: ErrorType) -> bool:
        """Determine if error type should be retried"""
        retryable_errors = {
            ErrorType.NETWORK_ERROR,
            ErrorType.TIMEOUT_ERROR,
            ErrorType.API_SERVER_ERROR,
            ErrorType.UNKNOWN_ERROR
        }
        return error_type in retryable_errors
    
    def _calculate_retry_delay(self, retry_config: RetryConfig, attempt: int) -> float:
        """Calculate delay for retry attempt"""
        if retry_config.strategy == RetryStrategy.IMMEDIATE:
            return 0.0
        elif retry_config.strategy == RetryStrategy.FIXED_DELAY:
            delay = retry_config.base_delay
        elif retry_config.strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = retry_config.base_delay * (attempt + 1)
        elif retry_config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = retry_config.base_delay * (2 ** attempt)
        else:
            delay = retry_config.base_delay
        
        # Apply jitter if enabled
        if retry_config.jitter:
            delay *= (0.5 + random.random() * 0.5)
        
        # Cap at max delay
        return min(delay, retry_config.max_delay)
    
    def _is_circuit_closed(self, service_name: str) -> bool:
        """Check if circuit breaker is closed (allowing requests)"""
        if service_name not in self.circuit_breakers:
            return True
        
        breaker = self.circuit_breakers[service_name]
        config = breaker["config"]
        
        if breaker["state"] == CircuitBreakerState.CLOSED:
            return True
        elif breaker["state"] == CircuitBreakerState.OPEN:
            # Check if recovery timeout has passed
            if (breaker["last_failure_time"] and 
                datetime.now() - breaker["last_failure_time"] > timedelta(seconds=config.recovery_timeout)):
                breaker["state"] = CircuitBreakerState.HALF_OPEN
                breaker["success_count"] = 0
                logger.info(f"Circuit breaker for {service_name} moved to HALF_OPEN")
                return True
            return False
        elif breaker["state"] == CircuitBreakerState.HALF_OPEN:
            return True
        
        return False
    
    async def _try_alternatives(self, 
                               service_name: str, 
                               operation: Callable, 
                               *args, 
                               **kwargs) -> Dict[str, Any]:
        """Try alternative services when primary fails"""
        alternatives = self.alternative_sources.get(service_name, [])
        
        for alt_service in alternatives:
            if self._is_circuit_closed(alt_service):
                try:
                    logger.info(f"Trying alternative service: {alt_service}")
                    
                    # Modify operation for alternative service if needed
                    alt_operation = self._adapt_operation_for_service(operation, alt_service)
                    
                    result = await self.execute_with_recovery(alt_service, alt_operation, *args, **kwargs)
                    
                    if result.get("type") == "success":
                        return {
                            "type": "success",
                            "data": result["data"],
                            "service": alt_service,
                            "is_alternative": True,
                            "original_service": service_name
                        }
                        
                except Exception as e:
                    logger.warning(f"Alternative service {alt_service} also failed: {e}")
                    continue
        
        # All alternatives failed, return cached response if available
        cached_result = self._get_any_cached_response(service_name)
        if cached_result:
            logger.info(f"Returning stale cached response for {service_name}")
            return {
                "type": "success",
                "data": cached_result,
                "service": service_name,
                "is_cached": True,
                "is_stale": True
            }
        
        # Return graceful degradation response
        return self._get_graceful_degradation_response(service_name)
    
    def _adapt_operation_for_service(self, operation: Callable, service_name: str) -> Callable:
        """Adapt operation for alternative service"""
        # This would contain service-specific adaptations
        # For now, return the same operation
        return operation
    
    def _get_graceful_degradation_response(self, service_name: str) -> Dict[str, Any]:
        """Provide graceful degradation when all services fail"""
        degradation_responses = {
            "coingecko": {
                "type": "degraded",
                "message": "Price data is temporarily unavailable. Please try again in a few minutes.",
                "suggestion": "You can check prices on major exchanges like Binance or Coinbase.",
                "service": service_name
            },
            "defillama": {
                "type": "degraded",
                "message": "DeFi data is temporarily unavailable. Please try again later.",
                "suggestion": "You can check protocol information on their official websites.",
                "service": service_name
            },
            "groq": {
                "type": "degraded",
                "message": "AI response is temporarily unavailable. Please rephrase your question or try again.",
                "suggestion": "Try asking a simpler question or check our help section.",
                "service": service_name
            }
        }
        
        return degradation_responses.get(service_name, {
            "type": "degraded",
            "message": f"Service {service_name} is temporarily unavailable.",
            "suggestion": "Please try again in a few minutes.",
            "service": service_name
        })
    
    def _generate_cache_key(self, service_name: str, args: tuple, kwargs: dict) -> str:
        """Generate cache key for request"""
        import hashlib
        
        # Create a string representation of the request
        request_str = f"{service_name}:{str(args)}:{str(sorted(kwargs.items()))}"
        
        # Generate hash
        return hashlib.md5(request_str.encode()).hexdigest()
    
    def _cache_response(self, service_name: str, cache_key: str, response: Any):
        """Cache response with TTL"""
        if service_name not in self.cached_responses:
            self.cached_responses[service_name] = {}
        
        self.cached_responses[service_name][cache_key] = {
            "data": response,
            "timestamp": datetime.now(),
            "ttl": self.cache_ttl[service_name]
        }
    
    def _get_cached_response(self, service_name: str, cache_key: str) -> Optional[Any]:
        """Get cached response if still valid"""
        if (service_name not in self.cached_responses or 
            cache_key not in self.cached_responses[service_name]):
            return None
        
        cached_item = self.cached_responses[service_name][cache_key]
        
        # Check if cache is still valid
        age = (datetime.now() - cached_item["timestamp"]).total_seconds()
        if age < cached_item["ttl"]:
            return cached_item["data"]
        
        # Cache expired, remove it
        del self.cached_responses[service_name][cache_key]
        return None
    
    def _get_any_cached_response(self, service_name: str) -> Optional[Any]:
        """Get any cached response, even if stale"""
        if service_name not in self.cached_responses:
            return None
        
        # Return the most recent cached response
        cached_items = self.cached_responses[service_name].values()
        if cached_items:
            most_recent = max(cached_items, key=lambda x: x["timestamp"])
            return most_recent["data"]
        
        return None
    
    def _get_retry_config(self, service_name: str) -> RetryConfig:
        """Get retry configuration for service"""
        # Default retry config
        default_config = RetryConfig()
        
        # Service-specific configs would be loaded here
        service_configs = {
            "coingecko": RetryConfig(max_retries=2, strategy=RetryStrategy.EXPONENTIAL_BACKOFF),
            "defillama": RetryConfig(max_retries=3, strategy=RetryStrategy.EXPONENTIAL_BACKOFF),
            "groq": RetryConfig(max_retries=1, strategy=RetryStrategy.IMMEDIATE),
            "openai": RetryConfig(max_retries=2, strategy=RetryStrategy.LINEAR_BACKOFF),
        }
        
        return service_configs.get(service_name, default_config)
    
    async def _record_success(self, service_name: str, response_time: float):
        """Record successful operation"""
        # Update circuit breaker
        if service_name in self.circuit_breakers:
            breaker = self.circuit_breakers[service_name]
            breaker["failure_count"] = 0
            
            if breaker["state"] == CircuitBreakerState.HALF_OPEN:
                breaker["success_count"] += 1
                if breaker["success_count"] >= breaker["config"].success_threshold:
                    breaker["state"] = CircuitBreakerState.CLOSED
                    logger.info(f"Circuit breaker for {service_name} closed after recovery")
        
        # Update service health
        if service_name in self.service_health:
            health = self.service_health[service_name]
            health.is_healthy = True
            health.last_success = datetime.now()
            health.consecutive_failures = 0
            health.consecutive_successes += 1
            health.total_requests += 1
            health.successful_requests += 1
            health.circuit_breaker_state = self.circuit_breakers[service_name]["state"]
            
            # Update average response time
            if health.avg_response_time == 0:
                health.avg_response_time = response_time
            else:
                health.avg_response_time = (health.avg_response_time * 0.9) + (response_time * 0.1)
    
    async def _record_error(self, 
                          service_name: str, 
                          error_type: ErrorType, 
                          error_message: str, 
                          retry_count: int, 
                          context: Dict[str, Any]):
        """Record error occurrence"""
        
        error_id = f"{service_name}_{int(time.time())}_{retry_count}"
        
        error_record = ErrorRecord(
            error_id=error_id,
            service_name=service_name,
            error_type=error_type,
            error_message=error_message,
            timestamp=datetime.now(),
            context=context,
            retry_count=retry_count,
            resolved=False,
            resolution_time=None
        )
        
        # Store in memory
        self.error_history.append(error_record)
        
        # Store in database
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO error_records 
                    (error_id, service_name, error_type, error_message, timestamp, 
                     context, retry_count, resolved, resolution_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    error_record.error_id,
                    error_record.service_name,
                    error_record.error_type.value,
                    error_record.error_message,
                    error_record.timestamp.isoformat(),
                    json.dumps(error_record.context),
                    error_record.retry_count,
                    error_record.resolved,
                    error_record.resolution_time.isoformat() if error_record.resolution_time else None
                ))
        except Exception as e:
            logger.error(f"Failed to store error record: {e}")
        
        # Update circuit breaker
        if service_name in self.circuit_breakers:
            breaker = self.circuit_breakers[service_name]
            breaker["failure_count"] += 1
            breaker["last_failure_time"] = datetime.now()
            
            if breaker["failure_count"] >= breaker["config"].failure_threshold:
                breaker["state"] = CircuitBreakerState.OPEN
                logger.warning(f"Circuit breaker opened for {service_name} after {breaker['failure_count']} failures")
        
        # Update service health
        if service_name in self.service_health:
            health = self.service_health[service_name]
            health.last_failure = datetime.now()
            health.consecutive_failures += 1
            health.consecutive_successes = 0
            health.total_requests += 1
            health.failed_requests += 1
            health.circuit_breaker_state = self.circuit_breakers[service_name]["state"]
            
            # Mark as unhealthy if too many consecutive failures
            if health.consecutive_failures >= 3:
                health.is_healthy = False
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status"""
        health_status = {
            "overall_health": "healthy",
            "services": {},
            "error_summary": {},
            "recommendations": []
        }
        
        unhealthy_services = 0
        total_services = len(self.service_health)
        
        for service_name, health in self.service_health.items():
            health_status["services"][service_name] = {
                "is_healthy": health.is_healthy,
                "circuit_breaker_state": health.circuit_breaker_state.value,
                "consecutive_failures": health.consecutive_failures,
                "success_rate": (health.successful_requests / max(health.total_requests, 1)) * 100,
                "avg_response_time": health.avg_response_time,
                "last_success": health.last_success.isoformat() if health.last_success else None,
                "last_failure": health.last_failure.isoformat() if health.last_failure else None
            }
            
            if not health.is_healthy:
                unhealthy_services += 1
        
        # Determine overall health
        if unhealthy_services == 0:
            health_status["overall_health"] = "healthy"
        elif unhealthy_services < total_services / 2:
            health_status["overall_health"] = "degraded"
        else:
            health_status["overall_health"] = "unhealthy"
        
        # Error summary
        recent_errors = [e for e in self.error_history if 
                        (datetime.now() - e.timestamp).total_seconds() < 3600]  # Last hour
        
        error_counts = defaultdict(int)
        for error in recent_errors:
            error_counts[error.error_type.value] += 1
        
        health_status["error_summary"] = dict(error_counts)
        
        # Recommendations
        if unhealthy_services > 0:
            health_status["recommendations"].append("Some services are experiencing issues. Alternative sources are being used.")
        
        if error_counts.get("api_rate_limit", 0) > 5:
            health_status["recommendations"].append("High rate limiting detected. Consider reducing request frequency.")
        
        if error_counts.get("timeout_error", 0) > 3:
            health_status["recommendations"].append("Network timeouts detected. Check internet connection.")
        
        return health_status
    
    async def force_circuit_breaker_reset(self, service_name: str):
        """Manually reset circuit breaker for a service"""
        if service_name in self.circuit_breakers:
            self.circuit_breakers[service_name]["state"] = CircuitBreakerState.CLOSED
            self.circuit_breakers[service_name]["failure_count"] = 0
            self.circuit_breakers[service_name]["success_count"] = 0
            logger.info(f"Circuit breaker manually reset for {service_name}")
    
    async def clear_cache(self, service_name: Optional[str] = None):
        """Clear cache for specific service or all services"""
        if service_name:
            if service_name in self.cached_responses:
                self.cached_responses[service_name].clear()
                logger.info(f"Cache cleared for {service_name}")
        else:
            self.cached_responses.clear()
            logger.info("All caches cleared")

# Global instance
error_recovery_system = ErrorRecoverySystem()

async def execute_with_recovery(service_name: str, operation: Callable, *args, **kwargs) -> Dict[str, Any]:
    """Execute operation with comprehensive error recovery"""
    return await error_recovery_system.execute_with_recovery(service_name, operation, *args, **kwargs)

async def get_system_health() -> Dict[str, Any]:
    """Get system health status"""
    return await error_recovery_system.get_system_health()

async def reset_circuit_breaker(service_name: str):
    """Reset circuit breaker for a service"""
    await error_recovery_system.force_circuit_breaker_reset(service_name)

async def clear_service_cache(service_name: Optional[str] = None):
    """Clear cache for service"""
    await error_recovery_system.clear_cache(service_name)