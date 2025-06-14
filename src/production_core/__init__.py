"""
Production Core Module - Industrial Grade Infrastructure
========================================================

This module provides enterprise-grade infrastructure components for the Möbius AI Assistant:

- Advanced caching with multi-tier architecture
- Circuit breakers and resilience patterns
- Comprehensive monitoring and metrics
- Security enhancements and rate limiting
- Performance optimization and resource management
- Health checks and self-healing capabilities

All components are designed for production environments with high availability,
scalability, and reliability requirements.
"""

from .cache_manager import IntelligentCacheManager
from .circuit_breaker import CircuitBreaker
from .rate_limiter import RateLimiter
from .health_monitor import HealthMonitor
from .metrics_collector import MetricCollector
from .security_manager import SecurityManager
from .performance_optimizer import PerformanceOptimizer

__all__ = [
    'IntelligentCacheManager',
    'CircuitBreaker', 
    'RateLimiter',
    'HealthMonitor',
    'MetricCollector',
    'SecurityManager',
    'PerformanceOptimizer'
]

__version__ = "1.0.0"
__author__ = "Möbius AI Team"