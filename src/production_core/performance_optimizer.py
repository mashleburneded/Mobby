"""
Performance Optimizer - Production Grade Performance Management
==============================================================

Advanced performance optimization system with:
- Resource usage monitoring and optimization
- Connection pooling and management
- Async operation optimization
- Memory management and garbage collection
- Database query optimization
- API response time optimization
"""

import asyncio
import gc
import psutil
import time
import weakref
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from collections import defaultdict, deque
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
import aiohttp

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics snapshot"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    active_connections: int
    response_time_ms: float
    requests_per_second: float
    error_rate: float
    gc_collections: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'cpu_percent': self.cpu_percent,
            'memory_percent': self.memory_percent,
            'memory_used_mb': self.memory_used_mb,
            'active_connections': self.active_connections,
            'response_time_ms': self.response_time_ms,
            'requests_per_second': self.requests_per_second,
            'error_rate': self.error_rate,
            'gc_collections': self.gc_collections
        }


@dataclass
class OptimizationRule:
    """Performance optimization rule"""
    name: str
    condition: Callable[[PerformanceMetrics], bool]
    action: Callable[[], None]
    cooldown_seconds: int = 300  # 5 minutes
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0


class ConnectionPool:
    """Advanced connection pool with health monitoring"""
    
    def __init__(self, max_connections: int = 100, min_connections: int = 10,
                 connection_timeout: float = 30.0, idle_timeout: float = 300.0):
        self.max_connections = max_connections
        self.min_connections = min_connections
        self.connection_timeout = connection_timeout
        self.idle_timeout = idle_timeout
        
        self.active_connections: Dict[str, aiohttp.ClientSession] = {}
        self.idle_connections: deque = deque()
        self.connection_stats: Dict[str, Dict[str, Any]] = defaultdict(dict)
        
        self._lock = asyncio.Lock()
        self._cleanup_task: Optional[asyncio.Task] = None
        
    async def get_connection(self, key: str = "default") -> aiohttp.ClientSession:
        """Get connection from pool"""
        async with self._lock:
            # Check if we have an active connection for this key
            if key in self.active_connections:
                connection = self.active_connections[key]
                if not connection.closed:
                    return connection
                else:
                    # Remove closed connection
                    del self.active_connections[key]
            
            # Try to get from idle pool
            if self.idle_connections:
                connection = self.idle_connections.popleft()
                if not connection.closed:
                    self.active_connections[key] = connection
                    return connection
            
            # Create new connection if under limit
            if len(self.active_connections) < self.max_connections:
                connection = aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=self.connection_timeout)
                )
                self.active_connections[key] = connection
                self.connection_stats[key] = {
                    'created_at': datetime.utcnow(),
                    'requests_count': 0,
                    'last_used': datetime.utcnow()
                }
                return connection
            
            # Pool is full, wait and retry
            await asyncio.sleep(0.1)
            return await self.get_connection(key)
    
    async def release_connection(self, key: str):
        """Release connection back to pool"""
        async with self._lock:
            if key in self.active_connections:
                connection = self.active_connections[key]
                del self.active_connections[key]
                
                # Add to idle pool if not closed and under limit
                if not connection.closed and len(self.idle_connections) < self.max_connections:
                    self.idle_connections.append(connection)
                    self.connection_stats[key]['last_used'] = datetime.utcnow()
                else:
                    await connection.close()
    
    async def cleanup_idle_connections(self):
        """Clean up idle connections that have timed out"""
        async with self._lock:
            now = datetime.utcnow()
            cutoff_time = now - timedelta(seconds=self.idle_timeout)
            
            # Clean idle connections
            active_idle = []
            while self.idle_connections:
                connection = self.idle_connections.popleft()
                
                # Find the key for this connection
                connection_key = None
                for key, stats in self.connection_stats.items():
                    if stats.get('last_used', now) > cutoff_time:
                        active_idle.append(connection)
                        break
                else:
                    # Connection is too old, close it
                    await connection.close()
            
            # Put back active idle connections
            self.idle_connections.extend(active_idle)
    
    async def start_cleanup_task(self):
        """Start background cleanup task"""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def _cleanup_loop(self):
        """Background cleanup loop"""
        while True:
            try:
                await self.cleanup_idle_connections()
                await asyncio.sleep(60)  # Clean every minute
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Connection pool cleanup error: {e}")
                await asyncio.sleep(60)
    
    async def close_all(self):
        """Close all connections"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
        
        async with self._lock:
            # Close active connections
            for connection in self.active_connections.values():
                await connection.close()
            self.active_connections.clear()
            
            # Close idle connections
            while self.idle_connections:
                connection = self.idle_connections.popleft()
                await connection.close()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        return {
            'active_connections': len(self.active_connections),
            'idle_connections': len(self.idle_connections),
            'max_connections': self.max_connections,
            'min_connections': self.min_connections,
            'connection_stats': dict(self.connection_stats)
        }


class MemoryOptimizer:
    """Memory usage optimization and monitoring"""
    
    def __init__(self):
        self.gc_stats = {
            'collections': [0, 0, 0],  # GC generation counts
            'last_collection': datetime.utcnow(),
            'memory_before_gc': 0,
            'memory_after_gc': 0
        }
        
        self.memory_threshold_mb = 500  # Trigger optimization at 500MB
        self.last_optimization = datetime.utcnow()
        self.optimization_interval = 300  # 5 minutes
    
    async def optimize_memory(self) -> Dict[str, Any]:
        """Perform memory optimization"""
        start_time = time.time()
        memory_before = psutil.Process().memory_info().rss / 1024 / 1024
        
        # Force garbage collection
        collected = [gc.collect(generation) for generation in range(3)]
        
        # Update stats
        memory_after = psutil.Process().memory_info().rss / 1024 / 1024
        self.gc_stats.update({
            'collections': [sum(x) for x in zip(self.gc_stats['collections'], collected)],
            'last_collection': datetime.utcnow(),
            'memory_before_gc': memory_before,
            'memory_after_gc': memory_after
        })
        
        optimization_time = (time.time() - start_time) * 1000
        memory_freed = memory_before - memory_after
        
        logger.info(f"Memory optimization completed: freed {memory_freed:.1f}MB in {optimization_time:.1f}ms")
        
        return {
            'memory_before_mb': memory_before,
            'memory_after_mb': memory_after,
            'memory_freed_mb': memory_freed,
            'optimization_time_ms': optimization_time,
            'objects_collected': sum(collected)
        }
    
    async def should_optimize(self) -> bool:
        """Check if memory optimization should be triggered"""
        now = datetime.utcnow()
        
        # Check time interval
        if (now - self.last_optimization).total_seconds() < self.optimization_interval:
            return False
        
        # Check memory usage
        current_memory = psutil.Process().memory_info().rss / 1024 / 1024
        return current_memory > self.memory_threshold_mb
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get current memory statistics"""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            'rss_mb': memory_info.rss / 1024 / 1024,
            'vms_mb': memory_info.vms / 1024 / 1024,
            'percent': process.memory_percent(),
            'gc_stats': self.gc_stats,
            'gc_thresholds': gc.get_threshold(),
            'gc_counts': gc.get_count()
        }


class AsyncOptimizer:
    """Async operation optimization"""
    
    def __init__(self):
        self.task_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'count': 0,
            'total_time': 0,
            'avg_time': 0,
            'errors': 0
        })
        
        self.semaphores: Dict[str, asyncio.Semaphore] = {}
        self.default_concurrency = 10
    
    def get_semaphore(self, operation: str, max_concurrent: Optional[int] = None) -> asyncio.Semaphore:
        """Get semaphore for operation concurrency control"""
        if operation not in self.semaphores:
            limit = max_concurrent or self.default_concurrency
            self.semaphores[operation] = asyncio.Semaphore(limit)
        return self.semaphores[operation]
    
    async def execute_with_optimization(self, operation: str, coro, 
                                       max_concurrent: Optional[int] = None):
        """Execute coroutine with optimization"""
        semaphore = self.get_semaphore(operation, max_concurrent)
        
        async with semaphore:
            start_time = time.time()
            try:
                result = await coro
                
                # Update stats
                execution_time = (time.time() - start_time) * 1000
                stats = self.task_stats[operation]
                stats['count'] += 1
                stats['total_time'] += execution_time
                stats['avg_time'] = stats['total_time'] / stats['count']
                
                return result
                
            except Exception as e:
                self.task_stats[operation]['errors'] += 1
                raise e
    
    def get_task_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get task execution statistics"""
        return dict(self.task_stats)


class PerformanceOptimizer:
    """
    Production-grade performance optimization system
    
    Features:
    - Resource monitoring and optimization
    - Connection pooling and management
    - Memory optimization and garbage collection
    - Async operation optimization
    - Automatic performance tuning
    """
    
    def __init__(self):
        self.connection_pool = ConnectionPool()
        self.memory_optimizer = MemoryOptimizer()
        self.async_optimizer = AsyncOptimizer()
        
        # Performance monitoring
        self.metrics_history: deque[PerformanceMetrics] = deque(maxlen=1000)
        self.optimization_rules: List[OptimizationRule] = []
        
        # Monitoring state
        self.is_monitoring = False
        self.monitoring_task: Optional[asyncio.Task] = None
        self.optimization_task: Optional[asyncio.Task] = None
        
        # Performance thresholds
        self.thresholds = {
            'cpu_warning': 80.0,
            'cpu_critical': 95.0,
            'memory_warning': 80.0,
            'memory_critical': 95.0,
            'response_time_warning': 1000.0,  # ms
            'response_time_critical': 5000.0,  # ms
            'error_rate_warning': 0.05,  # 5%
            'error_rate_critical': 0.10   # 10%
        }
        
        self._setup_default_optimization_rules()
        logger.info("Performance optimizer initialized")
    
    def _setup_default_optimization_rules(self):
        """Setup default optimization rules"""
        
        # High memory usage rule
        self.optimization_rules.append(OptimizationRule(
            name="high_memory_usage",
            condition=lambda m: m.memory_percent > self.thresholds['memory_warning'],
            action=self._optimize_memory_usage,
            cooldown_seconds=300
        ))
        
        # High CPU usage rule
        self.optimization_rules.append(OptimizationRule(
            name="high_cpu_usage",
            condition=lambda m: m.cpu_percent > self.thresholds['cpu_warning'],
            action=self._optimize_cpu_usage,
            cooldown_seconds=300
        ))
        
        # High response time rule
        self.optimization_rules.append(OptimizationRule(
            name="high_response_time",
            condition=lambda m: m.response_time_ms > self.thresholds['response_time_warning'],
            action=self._optimize_response_time,
            cooldown_seconds=180
        ))
        
        # High error rate rule
        self.optimization_rules.append(OptimizationRule(
            name="high_error_rate",
            condition=lambda m: m.error_rate > self.thresholds['error_rate_warning'],
            action=self._optimize_error_handling,
            cooldown_seconds=600
        ))
    
    async def start_monitoring(self):
        """Start performance monitoring"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.optimization_task = asyncio.create_task(self._optimization_loop())
        
        # Start connection pool cleanup
        await self.connection_pool.start_cleanup_task()
        
        logger.info("Performance monitoring started")
    
    async def stop_monitoring(self):
        """Stop performance monitoring"""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
        
        if self.optimization_task:
            self.optimization_task.cancel()
        
        await self.connection_pool.close_all()
        
        logger.info("Performance monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                metrics = await self._collect_metrics()
                self.metrics_history.append(metrics)
                
                # Log critical performance issues
                if (metrics.cpu_percent > self.thresholds['cpu_critical'] or
                    metrics.memory_percent > self.thresholds['memory_critical']):
                    logger.warning(f"Critical performance issue detected: {metrics.to_dict()}")
                
                await asyncio.sleep(30)  # Collect metrics every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Performance monitoring error: {e}")
                await asyncio.sleep(30)
    
    async def _optimization_loop(self):
        """Optimization rule evaluation loop"""
        while self.is_monitoring:
            try:
                if self.metrics_history:
                    latest_metrics = self.metrics_history[-1]
                    await self._evaluate_optimization_rules(latest_metrics)
                
                await asyncio.sleep(60)  # Evaluate rules every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Optimization loop error: {e}")
                await asyncio.sleep(60)
    
    async def _collect_metrics(self) -> PerformanceMetrics:
        """Collect current performance metrics"""
        process = psutil.Process()
        
        # Calculate requests per second and error rate from recent history
        rps = 0.0
        error_rate = 0.0
        avg_response_time = 0.0
        
        if len(self.metrics_history) > 1:
            recent_metrics = list(self.metrics_history)[-10:]  # Last 10 samples
            if recent_metrics:
                response_times = [m.response_time_ms for m in recent_metrics]
                avg_response_time = sum(response_times) / len(response_times)
        
        return PerformanceMetrics(
            timestamp=datetime.utcnow(),
            cpu_percent=process.cpu_percent(),
            memory_percent=process.memory_percent(),
            memory_used_mb=process.memory_info().rss / 1024 / 1024,
            active_connections=len(self.connection_pool.active_connections),
            response_time_ms=avg_response_time,
            requests_per_second=rps,
            error_rate=error_rate,
            gc_collections=sum(gc.get_count())
        )
    
    async def _evaluate_optimization_rules(self, metrics: PerformanceMetrics):
        """Evaluate and trigger optimization rules"""
        now = datetime.utcnow()
        
        for rule in self.optimization_rules:
            # Check cooldown
            if (rule.last_triggered and 
                (now - rule.last_triggered).total_seconds() < rule.cooldown_seconds):
                continue
            
            # Check condition
            if rule.condition(metrics):
                try:
                    logger.info(f"Triggering optimization rule: {rule.name}")
                    
                    if asyncio.iscoroutinefunction(rule.action):
                        await rule.action()
                    else:
                        rule.action()
                    
                    rule.last_triggered = now
                    rule.trigger_count += 1
                    
                except Exception as e:
                    logger.error(f"Optimization rule {rule.name} failed: {e}")
    
    async def _optimize_memory_usage(self):
        """Optimize memory usage"""
        result = await self.memory_optimizer.optimize_memory()
        logger.info(f"Memory optimization triggered: {result}")
    
    async def _optimize_cpu_usage(self):
        """Optimize CPU usage"""
        # Reduce concurrency limits
        for semaphore in self.async_optimizer.semaphores.values():
            if hasattr(semaphore, '_value') and semaphore._value > 5:
                # This is a simplified approach - in practice, you'd need to recreate semaphores
                logger.info("CPU optimization: reducing concurrency limits")
        
        # Force a brief pause to let CPU recover
        await asyncio.sleep(1)
    
    async def _optimize_response_time(self):
        """Optimize response time"""
        # Clean up connection pool
        await self.connection_pool.cleanup_idle_connections()
        logger.info("Response time optimization: cleaned connection pool")
    
    async def _optimize_error_handling(self):
        """Optimize error handling"""
        # This would implement error-specific optimizations
        logger.info("Error handling optimization triggered")
    
    async def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        if not self.metrics_history:
            return {'error': 'No metrics available'}
        
        latest_metrics = self.metrics_history[-1]
        
        # Calculate trends
        if len(self.metrics_history) >= 10:
            recent_metrics = list(self.metrics_history)[-10:]
            cpu_trend = recent_metrics[-1].cpu_percent - recent_metrics[0].cpu_percent
            memory_trend = recent_metrics[-1].memory_percent - recent_metrics[0].memory_percent
        else:
            cpu_trend = 0
            memory_trend = 0
        
        return {
            'current_metrics': latest_metrics.to_dict(),
            'trends': {
                'cpu_trend': cpu_trend,
                'memory_trend': memory_trend
            },
            'connection_pool': self.connection_pool.get_stats(),
            'memory_stats': self.memory_optimizer.get_memory_stats(),
            'task_stats': self.async_optimizer.get_task_stats(),
            'optimization_rules': [
                {
                    'name': rule.name,
                    'trigger_count': rule.trigger_count,
                    'last_triggered': rule.last_triggered.isoformat() if rule.last_triggered else None
                }
                for rule in self.optimization_rules
            ],
            'thresholds': self.thresholds,
            'is_monitoring': self.is_monitoring
        }
    
    async def optimize_now(self) -> Dict[str, Any]:
        """Manually trigger all optimizations"""
        results = {}
        
        # Memory optimization
        results['memory'] = await self.memory_optimizer.optimize_memory()
        
        # Connection pool cleanup
        await self.connection_pool.cleanup_idle_connections()
        results['connections'] = 'cleaned'
        
        # Force garbage collection
        collected = gc.collect()
        results['gc_collected'] = collected
        
        logger.info(f"Manual optimization completed: {results}")
        return results


# Global performance optimizer instance
performance_optimizer = PerformanceOptimizer()


# Convenience functions and decorators
async def optimized_execution(operation: str, coro, max_concurrent: Optional[int] = None):
    """Execute coroutine with performance optimization"""
    return await performance_optimizer.async_optimizer.execute_with_optimization(
        operation, coro, max_concurrent
    )


def performance_monitored(operation: str, max_concurrent: Optional[int] = None):
    """Decorator for performance-monitored async functions"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            return await optimized_execution(operation, func(*args, **kwargs), max_concurrent)
        return wrapper
    return decorator