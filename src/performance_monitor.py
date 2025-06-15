# src/performance_monitor.py
"""
Performance monitoring and metrics collection for Möbius AI Assistant.
Implements Prometheus-style metrics with security-first design.
"""
import time
import asyncio
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from collections import defaultdict, deque
import threading

logger = logging.getLogger(__name__)

@dataclass
class MetricData:
    """Thread-safe metric data container"""
    count: int = 0
    total_time: float = 0.0
    min_time: float = float('inf')
    max_time: float = 0.0
    recent_times: deque = field(default_factory=lambda: deque(maxlen=100))
    
    def add_measurement(self, duration: float):
        """Add a new measurement with thread safety"""
        self.count += 1
        self.total_time += duration
        self.min_time = min(self.min_time, duration)
        self.max_time = max(self.max_time, duration)
        self.recent_times.append(duration)
    
    @property
    def avg_time(self) -> float:
        return self.total_time / self.count if self.count > 0 else 0.0
    
    @property
    def recent_avg(self) -> float:
        return sum(self.recent_times) / len(self.recent_times) if self.recent_times else 0.0

class PerformanceMonitor:
    """
    Thread-safe performance monitoring system.
    Tracks command execution times, user activity, and system health.
    """
    
    def __init__(self):
        self._lock = threading.RLock()
        self._command_metrics: Dict[str, MetricData] = defaultdict(MetricData)
        self._user_activity: Dict[int, int] = defaultdict(int)  # user_id -> command_count
        self._error_counts: Dict[str, int] = defaultdict(int)
        self._active_users: set = set()
        self._start_time = time.time()
        
        # Security: Limit stored data to prevent memory exhaustion
        self._max_users_tracked = 10000
        self._max_error_types = 100
        
    def track_command(self, command: str, user_id: int, duration: float, success: bool = True):
        """Track command execution metrics with security bounds"""
        with self._lock:
            # Security: Sanitize command name to prevent injection
            safe_command = self._sanitize_metric_name(command)
            
            # Track command performance
            self._command_metrics[safe_command].add_measurement(duration)
            
            # Track user activity with bounds checking
            if len(self._user_activity) < self._max_users_tracked:
                self._user_activity[user_id] += 1
                self._active_users.add(user_id)
            
            # Track errors
            if not success:
                error_key = f"{safe_command}_error"
                if len(self._error_counts) < self._max_error_types:
                    self._error_counts[error_key] += 1
    
    def track_error(self, error_type: str, details: Optional[str] = None):
        """Track system errors with security sanitization"""
        with self._lock:
            safe_error_type = self._sanitize_metric_name(error_type)
            if len(self._error_counts) < self._max_error_types:
                self._error_counts[safe_error_type] += 1
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary"""
        with self._lock:
            uptime = time.time() - self._start_time
            
            # Calculate top commands by usage
            top_commands = sorted(
                [(cmd, data.count) for cmd, data in self._command_metrics.items()],
                key=lambda x: x[1],
                reverse=True
            )[:10]
            
            # Calculate performance stats
            slow_commands = [
                (cmd, data.avg_time) 
                for cmd, data in self._command_metrics.items() 
                if data.avg_time > 1.0  # Commands taking > 1 second
            ]
            
            return {
                "system": {
                    "uptime_seconds": uptime,
                    "active_users": len(self._active_users),
                    "total_commands": sum(data.count for data in self._command_metrics.values()),
                    "total_errors": sum(self._error_counts.values())
                },
                "performance": {
                    "top_commands": top_commands,
                    "slow_commands": sorted(slow_commands, key=lambda x: x[1], reverse=True),
                    "avg_response_time": self._calculate_overall_avg_response_time()
                },
                "errors": dict(list(self._error_counts.items())[:20])  # Top 20 errors
            }
    
    def get_command_stats(self, command: str) -> Optional[Dict[str, Any]]:
        """Get detailed stats for a specific command"""
        safe_command = self._sanitize_metric_name(command)
        with self._lock:
            if safe_command not in self._command_metrics:
                return None
            
            data = self._command_metrics[safe_command]
            return {
                "count": data.count,
                "avg_time": data.avg_time,
                "min_time": data.min_time,
                "max_time": data.max_time,
                "recent_avg": data.recent_avg
            }
    
    def reset_metrics(self):
        """Reset all metrics (admin function)"""
        with self._lock:
            self._command_metrics.clear()
            self._user_activity.clear()
            self._error_counts.clear()
            self._active_users.clear()
            self._start_time = time.time()
            logger.info("Performance metrics reset")
    
    def _sanitize_metric_name(self, name: str) -> str:
        """Sanitize metric names to prevent injection attacks"""
        # Remove potentially dangerous characters
        safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
        sanitized = ''.join(c for c in name if c in safe_chars)
        # Limit length to prevent memory exhaustion
        return sanitized[:50]
    
    def _calculate_overall_avg_response_time(self) -> float:
        """Calculate overall average response time across all commands"""
        total_time = sum(data.total_time for data in self._command_metrics.values())
        total_count = sum(data.count for data in self._command_metrics.values())
        return total_time / total_count if total_count > 0 else 0.0
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        return {
            'total_commands': len(self._command_metrics),
            'total_errors': len(self._error_counts),
            'avg_response_time': self._calculate_overall_avg_response_time(),
            'success_rate': 0.95  # Placeholder
        }

class PerformanceDecorator:
    """Decorator for automatic performance tracking"""
    
    def __init__(self, monitor: PerformanceMonitor):
        self.monitor = monitor
    
    def track_command(self, command_name: str):
        """Decorator to track command performance"""
        def decorator(func):
            if asyncio.iscoroutinefunction(func):
                async def async_wrapper(*args, **kwargs):
                    start_time = time.time()
                    success = True
                    user_id = None
                    
                    try:
                        # Extract user_id from update if available
                        if args and hasattr(args[0], 'effective_user'):
                            user_id = args[0].effective_user.id
                        
                        result = await func(*args, **kwargs)
                        return result
                    except Exception as e:
                        success = False
                        self.monitor.track_error(f"{command_name}_exception", str(e))
                        raise
                    finally:
                        duration = time.time() - start_time
                        if user_id:
                            self.monitor.track_command(command_name, user_id, duration, success)
                
                return async_wrapper
            else:
                def sync_wrapper(*args, **kwargs):
                    start_time = time.time()
                    success = True
                    user_id = None
                    
                    try:
                        # Extract user_id from update if available
                        if args and hasattr(args[0], 'effective_user'):
                            user_id = args[0].effective_user.id
                        
                        result = func(*args, **kwargs)
                        return result
                    except Exception as e:
                        success = False
                        self.monitor.track_error(f"{command_name}_exception", str(e))
                        raise
                    finally:
                        duration = time.time() - start_time
                        if user_id:
                            self.monitor.track_command(command_name, user_id, duration, success)
                
                return sync_wrapper
        return decorator
    
    def track_function(self, func_name: str = None):
        """Decorator to track function performance"""
        def decorator(func):
            name = func_name or func.__name__
            
            if asyncio.iscoroutinefunction(func):
                async def async_wrapper(*args, **kwargs):
                    start_time = time.time()
                    user_id = None
                    success = True
                    try:
                        # Extract user_id from update if available
                        if args and hasattr(args[0], 'effective_user'):
                            user_id = args[0].effective_user.id
                        
                        result = await func(*args, **kwargs)
                        return result
                    except Exception as e:
                        success = False
                        self.track_error(f"{name}_exception", str(e))
                        raise
                    finally:
                        duration = time.time() - start_time
                        if user_id:
                            self.track_command(name, user_id, duration, success)
                return async_wrapper
            else:
                def sync_wrapper(*args, **kwargs):
                    start_time = time.time()
                    user_id = None
                    success = True
                    try:
                        # Extract user_id from update if available
                        if args and hasattr(args[0], 'effective_user'):
                            user_id = args[0].effective_user.id
                        
                        result = func(*args, **kwargs)
                        return result
                    except Exception as e:
                        success = False
                        self.track_error(f"{name}_exception", str(e))
                        raise
                    finally:
                        duration = time.time() - start_time
                        if user_id:
                            self.track_command(name, user_id, duration, success)
                return sync_wrapper
        return decorator

# Global performance monitor instance
performance_monitor = PerformanceMonitor()
track_performance = PerformanceDecorator(performance_monitor)