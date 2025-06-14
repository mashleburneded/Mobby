#!/usr/bin/env python3
"""
ENHANCED MONITORING & ALERTING SYSTEM
=====================================
Comprehensive monitoring with security alerts, performance metrics, and real-time dashboards.
"""

import asyncio
import logging
import time
import psutil
import json
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict, deque
import threading
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

@dataclass
class MetricPoint:
    """Single metric data point"""
    timestamp: float
    value: float
    tags: Dict[str, str]

@dataclass
class Alert:
    """Alert configuration and state"""
    name: str
    condition: str
    threshold: float
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    enabled: bool = True
    last_triggered: Optional[float] = None
    trigger_count: int = 0
    cooldown_seconds: int = 300  # 5 minutes

@dataclass
class SystemHealth:
    """System health metrics"""
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_io: Dict[str, int]
    process_count: int
    uptime_seconds: float
    load_average: List[float]

class MetricsCollector:
    """High-performance metrics collection system"""
    
    def __init__(self, max_points_per_metric: int = 1000):
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_points_per_metric))
        self.alerts: Dict[str, Alert] = {}
        self.alert_handlers: List[Callable] = []
        self.collection_interval = 10.0  # seconds
        self.is_collecting = False
        self.collection_task: Optional[asyncio.Task] = None
        self.lock = threading.Lock()
        
        # Performance counters
        self.counters = defaultdict(int)
        self.timers = defaultdict(list)
        
        # Security metrics
        self.security_events = deque(maxlen=1000)
        self.failed_logins = defaultdict(int)
        self.suspicious_activities = deque(maxlen=500)
        
        # Setup default alerts
        self._setup_default_alerts()
    
    def _setup_default_alerts(self):
        """Setup default system alerts"""
        default_alerts = [
            Alert("high_cpu", "cpu_percent > 80", 80.0, "HIGH"),
            Alert("high_memory", "memory_percent > 85", 85.0, "HIGH"),
            Alert("high_disk", "disk_percent > 90", 90.0, "CRITICAL"),
            Alert("too_many_errors", "error_rate > 10", 10.0, "MEDIUM"),
            Alert("slow_response", "avg_response_time > 5000", 5000.0, "MEDIUM"),
            Alert("failed_logins", "failed_login_rate > 5", 5.0, "HIGH"),
            Alert("memory_leak", "memory_growth_rate > 100", 100.0, "HIGH"),
            Alert("database_errors", "db_error_rate > 5", 5.0, "CRITICAL"),
            Alert("cache_miss_rate", "cache_miss_rate > 50", 50.0, "MEDIUM"),
            Alert("api_rate_limit", "api_rate_limit_hits > 100", 100.0, "HIGH")
        ]
        
        for alert in default_alerts:
            self.alerts[alert.name] = alert
    
    async def start_collection(self):
        """Start metrics collection"""
        if self.is_collecting:
            return
        
        self.is_collecting = True
        self.collection_task = asyncio.create_task(self._collection_loop())
        logger.info("✅ Metrics collection started")
    
    async def stop_collection(self):
        """Stop metrics collection"""
        self.is_collecting = False
        if self.collection_task:
            self.collection_task.cancel()
            try:
                await self.collection_task
            except asyncio.CancelledError:
                pass
        logger.info("✅ Metrics collection stopped")
    
    async def _collection_loop(self):
        """Main metrics collection loop"""
        while self.is_collecting:
            try:
                await self._collect_system_metrics()
                await self._collect_application_metrics()
                await self._check_alerts()
                await asyncio.sleep(self.collection_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in metrics collection: {e}")
                await asyncio.sleep(self.collection_interval)
    
    async def _collect_system_metrics(self):
        """Collect system-level metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            self.record_metric("system.cpu.percent", cpu_percent)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            self.record_metric("system.memory.percent", memory.percent)
            self.record_metric("system.memory.available", memory.available)
            self.record_metric("system.memory.used", memory.used)
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self.record_metric("system.disk.percent", disk_percent)
            self.record_metric("system.disk.free", disk.free)
            
            # Network metrics
            network = psutil.net_io_counters()
            self.record_metric("system.network.bytes_sent", network.bytes_sent)
            self.record_metric("system.network.bytes_recv", network.bytes_recv)
            
            # Process metrics
            process_count = len(psutil.pids())
            self.record_metric("system.processes.count", process_count)
            
            # Load average (Unix-like systems)
            try:
                load_avg = psutil.getloadavg()
                self.record_metric("system.load.1min", load_avg[0])
                self.record_metric("system.load.5min", load_avg[1])
                self.record_metric("system.load.15min", load_avg[2])
            except AttributeError:
                pass  # Not available on Windows
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
    
    async def _collect_application_metrics(self):
        """Collect application-specific metrics"""
        try:
            # Database metrics
            from secure_database_manager import secure_db_manager
            if secure_db_manager.pool:
                db_stats = await secure_db_manager.get_stats()
                pool_stats = db_stats.get('pool_stats', {})
                
                self.record_metric("app.database.connections.total", 
                                 pool_stats.get('total_connections', 0))
                self.record_metric("app.database.connections.available", 
                                 pool_stats.get('available_connections', 0))
                self.record_metric("app.database.queries.total", 
                                 pool_stats.get('query_stats', {}).get('total_queries', 0))
                self.record_metric("app.database.queries.failed", 
                                 pool_stats.get('query_stats', {}).get('failed_queries', 0))
                self.record_metric("app.database.avg_query_time", 
                                 pool_stats.get('query_stats', {}).get('avg_query_time', 0))
            
            # Cache metrics
            from secure_redis_cache import secure_cache
            if secure_cache.redis:
                cache_stats = await secure_cache.get_cache_stats()
                stats = cache_stats.get('cache_stats', {})
                
                self.record_metric("app.cache.hits", stats.get('hits', 0))
                self.record_metric("app.cache.misses", stats.get('misses', 0))
                self.record_metric("app.cache.errors", stats.get('errors', 0))
                self.record_metric("app.cache.avg_response_time", stats.get('avg_response_time', 0))
                
                # Calculate hit ratio
                total_requests = stats.get('hits', 0) + stats.get('misses', 0)
                hit_ratio = (stats.get('hits', 0) / max(total_requests, 1)) * 100
                self.record_metric("app.cache.hit_ratio", hit_ratio)
            
        except Exception as e:
            logger.error(f"Error collecting application metrics: {e}")
    
    def record_metric(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Record a metric value"""
        with self.lock:
            metric_point = MetricPoint(
                timestamp=time.time(),
                value=value,
                tags=tags or {}
            )
            self.metrics[name].append(metric_point)
    
    def increment_counter(self, name: str, value: int = 1, tags: Optional[Dict[str, str]] = None):
        """Increment a counter metric"""
        with self.lock:
            self.counters[name] += value
            self.record_metric(f"counter.{name}", self.counters[name], tags)
    
    @asynccontextmanager
    async def time_operation(self, operation_name: str, tags: Optional[Dict[str, str]] = None):
        """Context manager to time operations"""
        start_time = time.time()
        try:
            yield
        finally:
            duration = (time.time() - start_time) * 1000  # Convert to milliseconds
            self.record_metric(f"timer.{operation_name}", duration, tags)
            
            with self.lock:
                self.timers[operation_name].append(duration)
                # Keep only last 100 measurements
                if len(self.timers[operation_name]) > 100:
                    self.timers[operation_name] = self.timers[operation_name][-100:]
    
    def record_security_event(self, event_type: str, user_id: Optional[int], 
                            details: Dict[str, Any], severity: str = "MEDIUM"):
        """Record security event"""
        event = {
            'timestamp': time.time(),
            'type': event_type,
            'user_id': user_id,
            'details': details,
            'severity': severity
        }
        
        with self.lock:
            self.security_events.append(event)
        
        # Record as metric
        self.increment_counter(f"security.{event_type}")
        
        # Check for suspicious patterns
        self._analyze_security_patterns(event)
    
    def _analyze_security_patterns(self, event: Dict[str, Any]):
        """Analyze security events for suspicious patterns"""
        event_type = event['type']
        user_id = event.get('user_id')
        
        # Track failed logins
        if event_type == 'failed_login' and user_id:
            self.failed_logins[user_id] += 1
            
            # Alert on multiple failed logins
            if self.failed_logins[user_id] >= 5:
                self._trigger_alert("failed_logins", self.failed_logins[user_id])
        
        # Track suspicious activities
        suspicious_events = ['sql_injection_attempt', 'unauthorized_access', 'rate_limit_exceeded']
        if event_type in suspicious_events:
            with self.lock:
                self.suspicious_activities.append(event)
    
    async def _check_alerts(self):
        """Check all alert conditions"""
        for alert_name, alert in self.alerts.items():
            if not alert.enabled:
                continue
            
            try:
                should_trigger = await self._evaluate_alert_condition(alert)
                
                if should_trigger:
                    await self._trigger_alert(alert_name, alert)
                    
            except Exception as e:
                logger.error(f"Error checking alert {alert_name}: {e}")
    
    async def _evaluate_alert_condition(self, alert: Alert) -> bool:
        """Evaluate if alert condition is met"""
        # Get recent metrics for evaluation
        now = time.time()
        recent_window = 300  # 5 minutes
        
        # Simple condition evaluation (can be extended for complex conditions)
        if "cpu_percent" in alert.condition:
            recent_cpu = [p.value for p in self.metrics.get("system.cpu.percent", []) 
                         if now - p.timestamp < recent_window]
            if recent_cpu:
                avg_cpu = sum(recent_cpu) / len(recent_cpu)
                return avg_cpu > alert.threshold
        
        elif "memory_percent" in alert.condition:
            recent_memory = [p.value for p in self.metrics.get("system.memory.percent", []) 
                           if now - p.timestamp < recent_window]
            if recent_memory:
                avg_memory = sum(recent_memory) / len(recent_memory)
                return avg_memory > alert.threshold
        
        elif "disk_percent" in alert.condition:
            recent_disk = [p.value for p in self.metrics.get("system.disk.percent", []) 
                          if now - p.timestamp < recent_window]
            if recent_disk:
                avg_disk = sum(recent_disk) / len(recent_disk)
                return avg_disk > alert.threshold
        
        elif "error_rate" in alert.condition:
            error_count = self.counters.get("errors", 0)
            total_requests = self.counters.get("requests", 1)
            error_rate = (error_count / total_requests) * 100
            return error_rate > alert.threshold
        
        elif "cache_miss_rate" in alert.condition:
            hits = self.counters.get("cache_hits", 0)
            misses = self.counters.get("cache_misses", 0)
            total = hits + misses
            if total > 0:
                miss_rate = (misses / total) * 100
                return miss_rate > alert.threshold
        
        return False
    
    async def _trigger_alert(self, alert_name: str, value: Optional[float] = None):
        """Trigger an alert"""
        alert = self.alerts[alert_name]
        now = time.time()
        
        # Check cooldown
        if (alert.last_triggered and 
            now - alert.last_triggered < alert.cooldown_seconds):
            return
        
        # Update alert state
        alert.last_triggered = now
        alert.trigger_count += 1
        
        # Create alert message
        alert_data = {
            'name': alert_name,
            'severity': alert.severity,
            'condition': alert.condition,
            'threshold': alert.threshold,
            'current_value': value,
            'timestamp': now,
            'trigger_count': alert.trigger_count
        }
        
        logger.warning(f"🚨 ALERT TRIGGERED: {alert_name} - {alert.condition} (Value: {value})")
        
        # Send to alert handlers
        for handler in self.alert_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(alert_data)
                else:
                    handler(alert_data)
            except Exception as e:
                logger.error(f"Error in alert handler: {e}")
    
    def add_alert_handler(self, handler: Callable):
        """Add alert handler function"""
        self.alert_handlers.append(handler)
    
    def get_metrics_summary(self, time_window: int = 3600) -> Dict[str, Any]:
        """Get metrics summary for the specified time window"""
        now = time.time()
        cutoff = now - time_window
        
        summary = {
            'system': {},
            'application': {},
            'security': {},
            'alerts': {}
        }
        
        with self.lock:
            # System metrics
            for metric_name in ['system.cpu.percent', 'system.memory.percent', 'system.disk.percent']:
                recent_points = [p.value for p in self.metrics.get(metric_name, []) 
                               if p.timestamp > cutoff]
                if recent_points:
                    summary['system'][metric_name] = {
                        'avg': sum(recent_points) / len(recent_points),
                        'min': min(recent_points),
                        'max': max(recent_points),
                        'current': recent_points[-1] if recent_points else 0
                    }
            
            # Application metrics
            for metric_name in ['app.database.avg_query_time', 'app.cache.hit_ratio']:
                recent_points = [p.value for p in self.metrics.get(metric_name, []) 
                               if p.timestamp > cutoff]
                if recent_points:
                    summary['application'][metric_name] = {
                        'avg': sum(recent_points) / len(recent_points),
                        'current': recent_points[-1] if recent_points else 0
                    }
            
            # Security events
            recent_security_events = [e for e in self.security_events if e['timestamp'] > cutoff]
            summary['security'] = {
                'total_events': len(recent_security_events),
                'events_by_type': {},
                'events_by_severity': {}
            }
            
            for event in recent_security_events:
                event_type = event['type']
                severity = event['severity']
                summary['security']['events_by_type'][event_type] = \
                    summary['security']['events_by_type'].get(event_type, 0) + 1
                summary['security']['events_by_severity'][severity] = \
                    summary['security']['events_by_severity'].get(severity, 0) + 1
            
            # Alert summary
            summary['alerts'] = {
                'total_alerts': len(self.alerts),
                'enabled_alerts': len([a for a in self.alerts.values() if a.enabled]),
                'recent_triggers': len([a for a in self.alerts.values() 
                                      if a.last_triggered and a.last_triggered > cutoff])
            }
        
        return summary
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall system health status"""
        try:
            # Get latest system metrics
            latest_cpu = self.metrics.get("system.cpu.percent", [])
            latest_memory = self.metrics.get("system.memory.percent", [])
            latest_disk = self.metrics.get("system.disk.percent", [])
            
            cpu_value = latest_cpu[-1].value if latest_cpu else 0
            memory_value = latest_memory[-1].value if latest_memory else 0
            disk_value = latest_disk[-1].value if latest_disk else 0
            
            # Determine health status
            health_score = 100
            issues = []
            
            if cpu_value > 80:
                health_score -= 20
                issues.append(f"High CPU usage: {cpu_value:.1f}%")
            
            if memory_value > 85:
                health_score -= 25
                issues.append(f"High memory usage: {memory_value:.1f}%")
            
            if disk_value > 90:
                health_score -= 30
                issues.append(f"High disk usage: {disk_value:.1f}%")
            
            # Check recent errors
            recent_errors = self.counters.get("errors", 0)
            if recent_errors > 10:
                health_score -= 15
                issues.append(f"High error rate: {recent_errors} errors")
            
            # Determine status
            if health_score >= 90:
                status = "HEALTHY"
            elif health_score >= 70:
                status = "WARNING"
            elif health_score >= 50:
                status = "DEGRADED"
            else:
                status = "CRITICAL"
            
            return {
                'status': status,
                'health_score': max(0, health_score),
                'issues': issues,
                'metrics': {
                    'cpu_percent': cpu_value,
                    'memory_percent': memory_value,
                    'disk_percent': disk_value
                },
                'timestamp': time.time()
            }
            
        except Exception as e:
            logger.error(f"Error getting health status: {e}")
            return {
                'status': 'UNKNOWN',
                'health_score': 0,
                'issues': [f"Health check error: {str(e)}"],
                'timestamp': time.time()
            }

class TelegramAlertHandler:
    """Send alerts via Telegram"""
    
    def __init__(self, bot_token: str, admin_chat_ids: List[int]):
        self.bot_token = bot_token
        self.admin_chat_ids = admin_chat_ids
    
    async def handle_alert(self, alert_data: Dict[str, Any]):
        """Handle alert by sending Telegram message"""
        try:
            from telegram import Bot
            
            bot = Bot(token=self.bot_token)
            
            # Format alert message
            severity_emoji = {
                'LOW': '🟡',
                'MEDIUM': '🟠', 
                'HIGH': '🔴',
                'CRITICAL': '🚨'
            }
            
            emoji = severity_emoji.get(alert_data['severity'], '⚠️')
            
            message = (
                f"{emoji} **ALERT: {alert_data['name'].upper()}**\n\n"
                f"**Severity**: {alert_data['severity']}\n"
                f"**Condition**: {alert_data['condition']}\n"
                f"**Threshold**: {alert_data['threshold']}\n"
                f"**Current Value**: {alert_data.get('current_value', 'N/A')}\n"
                f"**Time**: {datetime.fromtimestamp(alert_data['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"**Trigger Count**: {alert_data['trigger_count']}"
            )
            
            # Send to all admin chats
            for chat_id in self.admin_chat_ids:
                await bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            logger.error(f"Error sending Telegram alert: {e}")

# Global monitoring instance
metrics_collector = MetricsCollector()

# Convenience functions
async def start_monitoring():
    """Start the monitoring system"""
    await metrics_collector.start_collection()

async def stop_monitoring():
    """Stop the monitoring system"""
    await metrics_collector.stop_collection()

def record_metric(name: str, value: float, tags: Optional[Dict[str, str]] = None):
    """Record a metric"""
    metrics_collector.record_metric(name, value, tags)

def increment_counter(name: str, value: int = 1, tags: Optional[Dict[str, str]] = None):
    """Increment a counter"""
    metrics_collector.increment_counter(name, value, tags)

def record_security_event(event_type: str, user_id: Optional[int], 
                         details: Dict[str, Any], severity: str = "MEDIUM"):
    """Record a security event"""
    metrics_collector.record_security_event(event_type, user_id, details, severity)

async def get_system_health() -> Dict[str, Any]:
    """Get system health status"""
    return metrics_collector.get_health_status()

def add_alert_handler(handler: Callable):
    """Add an alert handler"""
    metrics_collector.add_alert_handler(handler)