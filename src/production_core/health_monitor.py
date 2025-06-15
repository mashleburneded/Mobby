"""
Health Monitor - Production Grade System Health Monitoring
=========================================================

Comprehensive health monitoring system with:
- Service health checks and status tracking
- Performance metrics collection and analysis
- Automatic alerting and notification system
- Self-healing capabilities and recovery actions
- Resource usage monitoring and optimization
- Dependency health tracking
"""

import asyncio
import time
import psutil
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import weakref

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status levels"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class ServiceType(Enum):
    """Types of services to monitor"""
    DATABASE = "database"
    CACHE = "cache"
    API = "api"
    EXTERNAL_SERVICE = "external_service"
    BACKGROUND_TASK = "background_task"
    SYSTEM_RESOURCE = "system_resource"


@dataclass
class HealthCheckConfig:
    """Configuration for health checks"""
    interval_seconds: int = 30
    timeout_seconds: int = 10
    failure_threshold: int = 3
    recovery_threshold: int = 2
    enable_auto_recovery: bool = True
    alert_on_failure: bool = True
    alert_on_recovery: bool = True
    
    # Performance thresholds
    response_time_warning_ms: float = 1000
    response_time_critical_ms: float = 5000
    cpu_warning_percent: float = 80
    cpu_critical_percent: float = 95
    memory_warning_percent: float = 80
    memory_critical_percent: float = 95
    disk_warning_percent: float = 85
    disk_critical_percent: float = 95


@dataclass
class HealthCheckResult:
    """Result of a health check"""
    service_name: str
    status: HealthStatus
    response_time_ms: float
    timestamp: datetime
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    error: Optional[Exception] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'service_name': self.service_name,
            'status': self.status.value,
            'response_time_ms': self.response_time_ms,
            'timestamp': self.timestamp.isoformat(),
            'message': self.message,
            'details': self.details,
            'error': str(self.error) if self.error else None
        }


@dataclass
class ServiceHealth:
    """Health information for a service"""
    name: str
    service_type: ServiceType
    current_status: HealthStatus = HealthStatus.UNKNOWN
    last_check: Optional[datetime] = None
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    total_checks: int = 0
    total_failures: int = 0
    uptime_start: datetime = field(default_factory=datetime.utcnow)
    
    # Performance metrics
    avg_response_time_ms: float = 0
    min_response_time_ms: float = float('inf')
    max_response_time_ms: float = 0
    
    # Recent check history
    recent_checks: List[HealthCheckResult] = field(default_factory=list)
    
    def update_from_result(self, result: HealthCheckResult):
        """Update service health from check result"""
        self.last_check = result.timestamp
        self.total_checks += 1
        
        # Update status tracking
        if result.status == HealthStatus.HEALTHY:
            self.consecutive_failures = 0
            self.consecutive_successes += 1
        else:
            self.consecutive_successes = 0
            self.consecutive_failures += 1
            self.total_failures += 1
        
        self.current_status = result.status
        
        # Update performance metrics
        if result.response_time_ms > 0:
            self.avg_response_time_ms = (
                (self.avg_response_time_ms * (self.total_checks - 1) + result.response_time_ms) 
                / self.total_checks
            )
            self.min_response_time_ms = min(self.min_response_time_ms, result.response_time_ms)
            self.max_response_time_ms = max(self.max_response_time_ms, result.response_time_ms)
        
        # Keep recent check history (last 100 checks)
        self.recent_checks.append(result)
        if len(self.recent_checks) > 100:
            self.recent_checks.pop(0)
    
    def get_uptime_percentage(self) -> float:
        """Calculate uptime percentage"""
        if self.total_checks == 0:
            return 100.0
        return ((self.total_checks - self.total_failures) / self.total_checks) * 100
    
    def get_availability_sla(self, hours: int = 24) -> float:
        """Calculate SLA availability for specified time period"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_results = [
            check for check in self.recent_checks 
            if check.timestamp > cutoff_time
        ]
        
        if not recent_results:
            return 100.0
        
        healthy_checks = sum(1 for check in recent_results if check.status == HealthStatus.HEALTHY)
        return (healthy_checks / len(recent_results)) * 100


class SystemResourceMonitor:
    """Monitor system resources (CPU, memory, disk)"""
    
    def __init__(self, config: HealthCheckConfig):
        self.config = config
    
    async def check_cpu_usage(self) -> HealthCheckResult:
        """Check CPU usage"""
        start_time = time.time()
        
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            response_time = (time.time() - start_time) * 1000
            
            if cpu_percent >= self.config.cpu_critical_percent:
                status = HealthStatus.CRITICAL
                message = f"Critical CPU usage: {cpu_percent:.1f}%"
            elif cpu_percent >= self.config.cpu_warning_percent:
                status = HealthStatus.WARNING
                message = f"High CPU usage: {cpu_percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"CPU usage normal: {cpu_percent:.1f}%"
            
            return HealthCheckResult(
                service_name="system_cpu",
                status=status,
                response_time_ms=response_time,
                timestamp=datetime.utcnow(),
                message=message,
                details={'cpu_percent': cpu_percent}
            )
            
        except Exception as e:
            return HealthCheckResult(
                service_name="system_cpu",
                status=HealthStatus.CRITICAL,
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow(),
                message=f"Failed to check CPU usage: {e}",
                error=e
            )
    
    async def check_memory_usage(self) -> HealthCheckResult:
        """Check memory usage"""
        start_time = time.time()
        
        try:
            memory = psutil.virtual_memory()
            response_time = (time.time() - start_time) * 1000
            
            if memory.percent >= self.config.memory_critical_percent:
                status = HealthStatus.CRITICAL
                message = f"Critical memory usage: {memory.percent:.1f}%"
            elif memory.percent >= self.config.memory_warning_percent:
                status = HealthStatus.WARNING
                message = f"High memory usage: {memory.percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"Memory usage normal: {memory.percent:.1f}%"
            
            return HealthCheckResult(
                service_name="system_memory",
                status=status,
                response_time_ms=response_time,
                timestamp=datetime.utcnow(),
                message=message,
                details={
                    'memory_percent': memory.percent,
                    'memory_available_gb': memory.available / (1024**3),
                    'memory_total_gb': memory.total / (1024**3)
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                service_name="system_memory",
                status=HealthStatus.CRITICAL,
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow(),
                message=f"Failed to check memory usage: {e}",
                error=e
            )
    
    async def check_disk_usage(self) -> HealthCheckResult:
        """Check disk usage"""
        start_time = time.time()
        
        try:
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            response_time = (time.time() - start_time) * 1000
            
            if disk_percent >= self.config.disk_critical_percent:
                status = HealthStatus.CRITICAL
                message = f"Critical disk usage: {disk_percent:.1f}%"
            elif disk_percent >= self.config.disk_warning_percent:
                status = HealthStatus.WARNING
                message = f"High disk usage: {disk_percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"Disk usage normal: {disk_percent:.1f}%"
            
            return HealthCheckResult(
                service_name="system_disk",
                status=status,
                response_time_ms=response_time,
                timestamp=datetime.utcnow(),
                message=message,
                details={
                    'disk_percent': disk_percent,
                    'disk_free_gb': disk.free / (1024**3),
                    'disk_total_gb': disk.total / (1024**3)
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                service_name="system_disk",
                status=HealthStatus.CRITICAL,
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow(),
                message=f"Failed to check disk usage: {e}",
                error=e
            )


class HealthMonitor:
    """
    Production-grade health monitoring system
    
    Features:
    - Configurable health checks for multiple services
    - Automatic failure detection and recovery
    - Performance metrics collection
    - Alert system integration
    - Self-healing capabilities
    """
    
    def __init__(self, config: Optional[HealthCheckConfig] = None):
        self.config = config or HealthCheckConfig()
        self.services: Dict[str, ServiceHealth] = {}
        self.health_checks: Dict[str, Callable] = {}
        self.recovery_actions: Dict[str, Callable] = {}
        self.alert_handlers: List[Callable] = []
        
        # Monitoring tasks
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        self.is_monitoring = False
        
        # System resource monitor
        self.system_monitor = SystemResourceMonitor(self.config)
        
        # Metrics
        self.total_checks = 0
        self.total_failures = 0
        self.start_time = datetime.utcnow()
        
        logger.info("Health monitor initialized")
    
    def register_service(self, name: str, service_type: ServiceType, 
                        health_check: Callable, recovery_action: Optional[Callable] = None):
        """
        Register a service for health monitoring
        
        Args:
            name: Service name
            service_type: Type of service
            health_check: Async function that returns HealthCheckResult
            recovery_action: Optional async function for automatic recovery
        """
        self.services[name] = ServiceHealth(name, service_type)
        self.health_checks[name] = health_check
        
        if recovery_action:
            self.recovery_actions[name] = recovery_action
        
        logger.info(f"Registered service for monitoring: {name} ({service_type.value})")
    
    def add_alert_handler(self, handler: Callable[[HealthCheckResult], None]):
        """Add alert handler for health check failures"""
        self.alert_handlers.append(handler)
    
    async def start_monitoring(self):
        """Start health monitoring for all registered services"""
        if self.is_monitoring:
            logger.warning("Health monitoring already started")
            return
        
        self.is_monitoring = True
        
        # Start monitoring tasks for each service
        for service_name in self.services.keys():
            task = asyncio.create_task(self._monitor_service(service_name))
            self.monitoring_tasks[service_name] = task
        
        # Start system resource monitoring
        system_tasks = [
            asyncio.create_task(self._monitor_system_resource("cpu")),
            asyncio.create_task(self._monitor_system_resource("memory")),
            asyncio.create_task(self._monitor_system_resource("disk"))
        ]
        
        for i, task in enumerate(system_tasks):
            self.monitoring_tasks[f"system_{['cpu', 'memory', 'disk'][i]}"] = task
        
        logger.info(f"Started health monitoring for {len(self.services)} services")
    
    async def stop_monitoring(self):
        """Stop health monitoring"""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        
        # Cancel all monitoring tasks
        for task in self.monitoring_tasks.values():
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.monitoring_tasks.values(), return_exceptions=True)
        self.monitoring_tasks.clear()
        
        logger.info("Health monitoring stopped")
    
    async def _monitor_service(self, service_name: str):
        """Monitor a specific service"""
        while self.is_monitoring:
            try:
                # Perform health check
                health_check = self.health_checks[service_name]
                result = await asyncio.wait_for(
                    health_check(),
                    timeout=self.config.timeout_seconds
                )
                
                # Update service health
                service = self.services[service_name]
                service.update_from_result(result)
                
                # Update global metrics
                self.total_checks += 1
                if result.status != HealthStatus.HEALTHY:
                    self.total_failures += 1
                
                # Handle failure scenarios
                await self._handle_health_result(service, result)
                
            except asyncio.TimeoutError:
                # Health check timed out
                result = HealthCheckResult(
                    service_name=service_name,
                    status=HealthStatus.CRITICAL,
                    response_time_ms=self.config.timeout_seconds * 1000,
                    timestamp=datetime.utcnow(),
                    message=f"Health check timed out after {self.config.timeout_seconds}s"
                )
                
                service = self.services[service_name]
                service.update_from_result(result)
                await self._handle_health_result(service, result)
                
            except Exception as e:
                # Health check failed with exception
                result = HealthCheckResult(
                    service_name=service_name,
                    status=HealthStatus.CRITICAL,
                    response_time_ms=0,
                    timestamp=datetime.utcnow(),
                    message=f"Health check failed: {e}",
                    error=e
                )
                
                service = self.services[service_name]
                service.update_from_result(result)
                await self._handle_health_result(service, result)
                
                logger.error(f"Health check failed for {service_name}: {e}")
            
            # Wait for next check
            await asyncio.sleep(self.config.interval_seconds)
    
    async def _monitor_system_resource(self, resource_type: str):
        """Monitor system resources"""
        while self.is_monitoring:
            try:
                if resource_type == "cpu":
                    result = await self.system_monitor.check_cpu_usage()
                elif resource_type == "memory":
                    result = await self.system_monitor.check_memory_usage()
                elif resource_type == "disk":
                    result = await self.system_monitor.check_disk_usage()
                else:
                    continue
                
                # Register system service if not exists
                service_name = result.service_name
                if service_name not in self.services:
                    self.services[service_name] = ServiceHealth(service_name, ServiceType.SYSTEM_RESOURCE)
                
                # Update service health
                service = self.services[service_name]
                service.update_from_result(result)
                
                # Handle result
                await self._handle_health_result(service, result)
                
            except Exception as e:
                logger.error(f"System resource monitoring failed for {resource_type}: {e}")
            
            await asyncio.sleep(self.config.interval_seconds)
    
    async def _handle_health_result(self, service: ServiceHealth, result: HealthCheckResult):
        """Handle health check result and trigger actions"""
        
        # Check for failure threshold
        if (result.status != HealthStatus.HEALTHY and 
            service.consecutive_failures >= self.config.failure_threshold):
            
            # Trigger alerts
            if self.config.alert_on_failure:
                await self._send_alerts(result)
            
            # Attempt recovery
            if (self.config.enable_auto_recovery and 
                service.name in self.recovery_actions):
                await self._attempt_recovery(service.name)
        
        # Check for recovery
        elif (service.consecutive_successes >= self.config.recovery_threshold and
              service.total_failures > 0):
            
            if self.config.alert_on_recovery:
                recovery_result = HealthCheckResult(
                    service_name=service.name,
                    status=HealthStatus.HEALTHY,
                    response_time_ms=result.response_time_ms,
                    timestamp=datetime.utcnow(),
                    message=f"Service recovered after {service.consecutive_successes} successful checks"
                )
                await self._send_alerts(recovery_result)
    
    async def _send_alerts(self, result: HealthCheckResult):
        """Send alerts to registered handlers"""
        for handler in self.alert_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(result)
                else:
                    handler(result)
            except Exception as e:
                logger.error(f"Alert handler failed: {e}")
    
    async def _attempt_recovery(self, service_name: str):
        """Attempt automatic recovery for a service"""
        if service_name not in self.recovery_actions:
            return
        
        try:
            recovery_action = self.recovery_actions[service_name]
            logger.info(f"Attempting recovery for service: {service_name}")
            
            await recovery_action()
            logger.info(f"Recovery action completed for service: {service_name}")
            
        except Exception as e:
            logger.error(f"Recovery action failed for {service_name}: {e}")
    
    async def get_service_health(self, service_name: str) -> Optional[ServiceHealth]:
        """Get health information for a specific service"""
        return self.services.get(service_name)
    
    async def get_overall_health(self) -> Dict[str, Any]:
        """Get overall system health summary"""
        healthy_services = sum(1 for service in self.services.values() 
                             if service.current_status == HealthStatus.HEALTHY)
        warning_services = sum(1 for service in self.services.values() 
                             if service.current_status == HealthStatus.WARNING)
        critical_services = sum(1 for service in self.services.values() 
                              if service.current_status == HealthStatus.CRITICAL)
        
        total_services = len(self.services)
        overall_status = HealthStatus.HEALTHY
        
        if critical_services > 0:
            overall_status = HealthStatus.CRITICAL
        elif warning_services > 0:
            overall_status = HealthStatus.WARNING
        
        uptime = datetime.utcnow() - self.start_time
        
        return {
            'overall_status': overall_status.value,
            'total_services': total_services,
            'healthy_services': healthy_services,
            'warning_services': warning_services,
            'critical_services': critical_services,
            'uptime_seconds': uptime.total_seconds(),
            'total_checks': self.total_checks,
            'total_failures': self.total_failures,
            'success_rate': ((self.total_checks - self.total_failures) / self.total_checks * 100) if self.total_checks > 0 else 100,
            'is_monitoring': self.is_monitoring
        }
    
    async def get_detailed_health_report(self) -> Dict[str, Any]:
        """Get detailed health report for all services"""
        overall_health = await self.get_overall_health()
        
        services_detail = {}
        for name, service in self.services.items():
            services_detail[name] = {
                'name': service.name,
                'type': service.service_type.value,
                'status': service.current_status.value,
                'last_check': service.last_check.isoformat() if service.last_check else None,
                'consecutive_failures': service.consecutive_failures,
                'consecutive_successes': service.consecutive_successes,
                'total_checks': service.total_checks,
                'total_failures': service.total_failures,
                'uptime_percentage': service.get_uptime_percentage(),
                'sla_24h': service.get_availability_sla(24),
                'avg_response_time_ms': service.avg_response_time_ms,
                'min_response_time_ms': service.min_response_time_ms if service.min_response_time_ms != float('inf') else 0,
                'max_response_time_ms': service.max_response_time_ms
            }
        
        return {
            'overall': overall_health,
            'services': services_detail,
            'timestamp': datetime.utcnow().isoformat()
        }


# Global health monitor instance
health_monitor = HealthMonitor()


# Example health check functions
async def database_health_check() -> HealthCheckResult:
    """Example database health check"""
    start_time = time.time()
    
    try:
        # Simulate database check
        await asyncio.sleep(0.1)  # Simulate query time
        
        response_time = (time.time() - start_time) * 1000
        
        return HealthCheckResult(
            service_name="database",
            status=HealthStatus.HEALTHY,
            response_time_ms=response_time,
            timestamp=datetime.utcnow(),
            message="Database connection successful"
        )
        
    except Exception as e:
        return HealthCheckResult(
            service_name="database",
            status=HealthStatus.CRITICAL,
            response_time_ms=(time.time() - start_time) * 1000,
            timestamp=datetime.utcnow(),
            message=f"Database connection failed: {e}",
            error=e
        )


async def cache_health_check() -> HealthCheckResult:
    """Example cache health check"""
    start_time = time.time()
    
    try:
        # Simulate cache check
        await asyncio.sleep(0.05)  # Simulate cache operation
        
        response_time = (time.time() - start_time) * 1000
        
        return HealthCheckResult(
            service_name="cache",
            status=HealthStatus.HEALTHY,
            response_time_ms=response_time,
            timestamp=datetime.utcnow(),
            message="Cache operational"
        )
        
    except Exception as e:
        return HealthCheckResult(
            service_name="cache",
            status=HealthStatus.CRITICAL,
            response_time_ms=(time.time() - start_time) * 1000,
            timestamp=datetime.utcnow(),
            message=f"Cache check failed: {e}",
            error=e
        )