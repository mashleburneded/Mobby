"""
Circuit Breaker Pattern Implementation
=====================================

Production-grade circuit breaker for resilience and fault tolerance:
- Automatic failure detection and recovery
- Configurable thresholds and timeouts
- Exponential backoff and jitter
- Health monitoring and metrics
- Self-healing capabilities
"""

import asyncio
import time
import random
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Optional, Union
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, rejecting requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker"""
    failure_threshold: int = 5          # Failures before opening
    recovery_timeout: int = 60          # Seconds before trying half-open
    success_threshold: int = 3          # Successes to close from half-open
    timeout: float = 30.0               # Request timeout in seconds
    expected_exception: type = Exception # Exception type to monitor
    
    # Advanced configuration
    sliding_window_size: int = 100      # Size of sliding window for metrics
    minimum_requests: int = 10          # Minimum requests before considering failure rate
    failure_rate_threshold: float = 0.5 # Failure rate threshold (0.0-1.0)
    exponential_backoff: bool = True    # Use exponential backoff
    max_backoff: int = 300              # Maximum backoff time in seconds
    jitter: bool = True                 # Add jitter to backoff


@dataclass
class RequestResult:
    """Result of a request through circuit breaker"""
    success: bool
    response: Any = None
    error: Optional[Exception] = None
    duration_ms: float = 0
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class SlidingWindow:
    """Sliding window for tracking request metrics"""
    
    def __init__(self, size: int):
        self.size = size
        self.results: list[RequestResult] = []
        self._lock = asyncio.Lock()
    
    async def add_result(self, result: RequestResult):
        """Add a request result to the window"""
        async with self._lock:
            self.results.append(result)
            if len(self.results) > self.size:
                self.results.pop(0)
    
    async def get_failure_rate(self) -> float:
        """Get current failure rate"""
        async with self._lock:
            if not self.results:
                return 0.0
            
            failures = sum(1 for result in self.results if not result.success)
            return failures / len(self.results)
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive metrics"""
        async with self._lock:
            if not self.results:
                return {
                    'total_requests': 0,
                    'failures': 0,
                    'successes': 0,
                    'failure_rate': 0.0,
                    'avg_duration_ms': 0.0
                }
            
            total = len(self.results)
            failures = sum(1 for result in self.results if not result.success)
            successes = total - failures
            avg_duration = sum(result.duration_ms for result in self.results) / total
            
            return {
                'total_requests': total,
                'failures': failures,
                'successes': successes,
                'failure_rate': failures / total,
                'avg_duration_ms': avg_duration
            }


class CircuitBreaker:
    """
    Production-grade circuit breaker implementation
    
    Provides automatic failure detection, recovery, and resilience patterns
    for external service calls and critical operations.
    """
    
    def __init__(self, name: str, config: Optional[CircuitBreakerConfig] = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        
        # State management
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.next_attempt_time: Optional[datetime] = None
        
        # Metrics and monitoring
        self.sliding_window = SlidingWindow(self.config.sliding_window_size)
        self.total_requests = 0
        self.total_failures = 0
        self.total_successes = 0
        self.state_changes = 0
        
        # Backoff management
        self.current_backoff = self.config.recovery_timeout
        
        # Thread safety
        self._lock = asyncio.Lock()
        
        logger.info(f"Circuit breaker '{name}' initialized with config: {self.config}")
    
    async def call(self, func: Callable, *args, **kwargs) -> RequestResult:
        """
        Execute function through circuit breaker
        
        Args:
            func: Async function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            RequestResult with success status and response/error
        """
        start_time = time.time()
        self.total_requests += 1
        
        # Check if circuit is open
        if await self._should_reject_request():
            error = Exception(f"Circuit breaker '{self.name}' is OPEN")
            result = RequestResult(
                success=False,
                error=error,
                duration_ms=(time.time() - start_time) * 1000
            )
            await self.sliding_window.add_result(result)
            logger.warning(f"Request rejected by circuit breaker '{self.name}'")
            raise error
        
        try:
            # Execute function with timeout
            response = await asyncio.wait_for(
                func(*args, **kwargs),
                timeout=self.config.timeout
            )
            
            # Record success
            duration_ms = (time.time() - start_time) * 1000
            result = RequestResult(
                success=True,
                response=response,
                duration_ms=duration_ms
            )
            
            await self._record_success(result)
            return result
            
        except asyncio.TimeoutError as e:
            # Handle timeout as failure
            duration_ms = (time.time() - start_time) * 1000
            timeout_error = Exception(f"Request timeout after {self.config.timeout}s")
            result = RequestResult(
                success=False,
                error=timeout_error,
                duration_ms=duration_ms
            )
            
            await self._record_failure(result)
            raise timeout_error
            
        except Exception as e:
            # Handle other exceptions
            duration_ms = (time.time() - start_time) * 1000
            result = RequestResult(
                success=False,
                error=e,
                duration_ms=duration_ms
            )
            
            # Only count as failure if it's the expected exception type
            if isinstance(e, self.config.expected_exception):
                await self._record_failure(result)
            else:
                await self.sliding_window.add_result(result)
            
            raise e
    
    async def _should_reject_request(self) -> bool:
        """Check if request should be rejected based on circuit state"""
        async with self._lock:
            now = datetime.utcnow()
            
            if self.state == CircuitState.CLOSED:
                return False
            
            elif self.state == CircuitState.OPEN:
                # Check if we should transition to half-open
                if self.next_attempt_time and now >= self.next_attempt_time:
                    await self._transition_to_half_open()
                    return False
                return True
            
            elif self.state == CircuitState.HALF_OPEN:
                # Allow limited requests in half-open state
                return False
            
            return False
    
    async def _record_success(self, result: RequestResult):
        """Record successful request"""
        async with self._lock:
            self.total_successes += 1
            await self.sliding_window.add_result(result)
            
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.config.success_threshold:
                    await self._transition_to_closed()
            
            elif self.state == CircuitState.CLOSED:
                # Reset failure count on success
                self.failure_count = 0
    
    async def _record_failure(self, result: RequestResult):
        """Record failed request"""
        async with self._lock:
            self.total_failures += 1
            self.failure_count += 1
            self.last_failure_time = datetime.utcnow()
            await self.sliding_window.add_result(result)
            
            if self.state == CircuitState.CLOSED:
                # Check if we should open the circuit
                await self._check_failure_threshold()
            
            elif self.state == CircuitState.HALF_OPEN:
                # Return to open state on any failure
                await self._transition_to_open()
    
    async def _check_failure_threshold(self):
        """Check if failure threshold is exceeded"""
        # Check simple failure count threshold
        if self.failure_count >= self.config.failure_threshold:
            await self._transition_to_open()
            return
        
        # Check failure rate threshold with sliding window
        metrics = await self.sliding_window.get_metrics()
        if (metrics['total_requests'] >= self.config.minimum_requests and
            metrics['failure_rate'] >= self.config.failure_rate_threshold):
            await self._transition_to_open()
    
    async def _transition_to_open(self):
        """Transition circuit to OPEN state"""
        if self.state != CircuitState.OPEN:
            self.state = CircuitState.OPEN
            self.state_changes += 1
            
            # Calculate next attempt time with backoff
            if self.config.exponential_backoff:
                self.current_backoff = min(
                    self.current_backoff * 2,
                    self.config.max_backoff
                )
            else:
                self.current_backoff = self.config.recovery_timeout
            
            # Add jitter if enabled
            if self.config.jitter:
                jitter_range = self.current_backoff * 0.1
                jitter = random.uniform(-jitter_range, jitter_range)
                backoff_with_jitter = max(1, self.current_backoff + jitter)
            else:
                backoff_with_jitter = self.current_backoff
            
            self.next_attempt_time = datetime.utcnow() + timedelta(seconds=backoff_with_jitter)
            
            logger.warning(
                f"Circuit breaker '{self.name}' opened. "
                f"Next attempt in {backoff_with_jitter:.1f}s"
            )
    
    async def _transition_to_half_open(self):
        """Transition circuit to HALF_OPEN state"""
        if self.state != CircuitState.HALF_OPEN:
            self.state = CircuitState.HALF_OPEN
            self.state_changes += 1
            self.success_count = 0
            self.failure_count = 0
            
            logger.info(f"Circuit breaker '{self.name}' transitioned to HALF_OPEN")
    
    async def _transition_to_closed(self):
        """Transition circuit to CLOSED state"""
        if self.state != CircuitState.CLOSED:
            self.state = CircuitState.CLOSED
            self.state_changes += 1
            self.failure_count = 0
            self.success_count = 0
            self.current_backoff = self.config.recovery_timeout  # Reset backoff
            
            logger.info(f"Circuit breaker '{self.name}' transitioned to CLOSED")
    
    async def force_open(self):
        """Manually force circuit to OPEN state"""
        async with self._lock:
            await self._transition_to_open()
            logger.warning(f"Circuit breaker '{self.name}' manually forced OPEN")
    
    async def force_closed(self):
        """Manually force circuit to CLOSED state"""
        async with self._lock:
            await self._transition_to_closed()
            logger.info(f"Circuit breaker '{self.name}' manually forced CLOSED")
    
    async def reset(self):
        """Reset circuit breaker to initial state"""
        async with self._lock:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.success_count = 0
            self.last_failure_time = None
            self.next_attempt_time = None
            self.current_backoff = self.config.recovery_timeout
            
            # Reset metrics
            self.sliding_window = SlidingWindow(self.config.sliding_window_size)
            
            logger.info(f"Circuit breaker '{self.name}' reset")
    
    def get_state(self) -> CircuitState:
        """Get current circuit state"""
        return self.state
    
    def is_closed(self) -> bool:
        """Check if circuit is closed (normal operation)"""
        return self.state == CircuitState.CLOSED
    
    def is_open(self) -> bool:
        """Check if circuit is open (failing)"""
        return self.state == CircuitState.OPEN
    
    def is_half_open(self) -> bool:
        """Check if circuit is half-open (testing)"""
        return self.state == CircuitState.HALF_OPEN
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive circuit breaker metrics"""
        window_metrics = await self.sliding_window.get_metrics()
        
        return {
            'name': self.name,
            'state': self.state.value,
            'failure_count': self.failure_count,
            'success_count': self.success_count,
            'total_requests': self.total_requests,
            'total_failures': self.total_failures,
            'total_successes': self.total_successes,
            'state_changes': self.state_changes,
            'current_backoff': self.current_backoff,
            'next_attempt_time': self.next_attempt_time.isoformat() if self.next_attempt_time else None,
            'last_failure_time': self.last_failure_time.isoformat() if self.last_failure_time else None,
            'window_metrics': window_metrics,
            'config': {
                'failure_threshold': self.config.failure_threshold,
                'recovery_timeout': self.config.recovery_timeout,
                'success_threshold': self.config.success_threshold,
                'timeout': self.config.timeout,
                'failure_rate_threshold': self.config.failure_rate_threshold
            }
        }


class CircuitBreakerManager:
    """Manager for multiple circuit breakers"""
    
    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self._lock = asyncio.Lock()
    
    async def get_circuit_breaker(self, name: str, config: Optional[CircuitBreakerConfig] = None) -> CircuitBreaker:
        """Get or create circuit breaker by name"""
        async with self._lock:
            if name not in self.circuit_breakers:
                self.circuit_breakers[name] = CircuitBreaker(name, config)
            return self.circuit_breakers[name]
    
    async def call_with_circuit_breaker(self, name: str, func: Callable, 
                                       config: Optional[CircuitBreakerConfig] = None,
                                       *args, **kwargs) -> RequestResult:
        """Execute function with named circuit breaker"""
        circuit_breaker = await self.get_circuit_breaker(name, config)
        return await circuit_breaker.call(func, *args, **kwargs)
    
    async def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get metrics for all circuit breakers"""
        metrics = {}
        for name, circuit_breaker in self.circuit_breakers.items():
            metrics[name] = await circuit_breaker.get_metrics()
        return metrics
    
    async def reset_all(self):
        """Reset all circuit breakers"""
        for circuit_breaker in self.circuit_breakers.values():
            await circuit_breaker.reset()
        logger.info("All circuit breakers reset")


# Global circuit breaker manager
circuit_breaker_manager = CircuitBreakerManager()


# Decorator for easy circuit breaker usage
def circuit_breaker(name: str, config: Optional[CircuitBreakerConfig] = None):
    """Decorator to wrap function with circuit breaker"""
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            return await circuit_breaker_manager.call_with_circuit_breaker(
                name, func, config, *args, **kwargs
            )
        return wrapper
    return decorator