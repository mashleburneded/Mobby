# src/health_monitor.py
"""
Health monitoring and status endpoints for Möbius AI Assistant.
Provides real-time health checks and system status without impacting performance.
"""
import asyncio
import time
import psutil
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import json

logger = logging.getLogger(__name__)

class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

@dataclass
class HealthCheck:
    name: str
    status: HealthStatus
    response_time_ms: float
    message: str
    details: Optional[Dict[str, Any]] = None

class HealthMonitor:
    """
    Lightweight health monitoring system that doesn't impact bot performance.
    Provides real-time status checks and system health metrics.
    """
    
    def __init__(self):
        self.health_checks = {}
        self.last_check_time = 0
        self.check_interval = 30  # 30 seconds
        self.cached_status = None
        
        # Health thresholds
        self.thresholds = {
            "cpu_percent": 80.0,
            "memory_percent": 85.0,
            "disk_percent": 90.0,
            "response_time_ms": 1000.0,
            "error_rate_percent": 5.0
        }
        
    async def get_health_status(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Get comprehensive health status with caching for performance"""
        current_time = time.time()
        
        # Use cached status if recent and not forcing refresh
        if (not force_refresh and 
            self.cached_status and 
            current_time - self.last_check_time < self.check_interval):
            return self.cached_status
        
        # Perform health checks
        health_checks = await self._run_health_checks()
        
        # Calculate overall status
        overall_status = self._calculate_overall_status(health_checks)
        
        # Get system metrics
        system_metrics = self._get_system_metrics()
        
        # Build status response
        status_response = {
            "timestamp": current_time,
            "overall_status": overall_status.value,
            "health_checks": [asdict(check) for check in health_checks],
            "system_metrics": system_metrics,
            "uptime_seconds": self._get_uptime(),
            "version": "Enhanced Edition v.a666.v01"
        }
        
        # Cache the result
        self.cached_status = status_response
        self.last_check_time = current_time
        
        return status_response
    
    async def _run_health_checks(self) -> List[HealthCheck]:
        """Run all health checks concurrently for speed"""
        checks = []
        
        # Database health check
        checks.append(await self._check_database_health())
        
        # AI provider health check
        checks.append(await self._check_ai_provider_health())
        
        # Memory health check
        checks.append(self._check_memory_health())
        
        # Disk space health check
        checks.append(self._check_disk_health())
        
        # Performance health check
        checks.append(await self._check_performance_health())
        
        return checks
    
    async def _check_database_health(self) -> HealthCheck:
        """Check database connectivity and performance"""
        start_time = time.time()
        
        try:
            from enhanced_db import enhanced_db
            
            # Simple query to test database
            result = enhanced_db.execute_query("SELECT 1 as test", fetch='one')
            response_time = (time.time() - start_time) * 1000
            
            if result.success and result.data and result.data.get('test') == 1:
                if response_time < self.thresholds["response_time_ms"]:
                    status = HealthStatus.HEALTHY
                    message = f"Database responsive ({response_time:.1f}ms)"
                else:
                    status = HealthStatus.DEGRADED
                    message = f"Database slow ({response_time:.1f}ms)"
            else:
                status = HealthStatus.UNHEALTHY
                message = "Database query failed"
            
            return HealthCheck(
                name="database",
                status=status,
                response_time_ms=response_time,
                message=message,
                details={"query_success": result.success, "execution_time": result.execution_time}
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheck(
                name="database",
                status=HealthStatus.UNHEALTHY,
                response_time_ms=response_time,
                message=f"Database error: {str(e)[:100]}",
                details={"error": str(e)}
            )
    
    async def _check_ai_provider_health(self) -> HealthCheck:
        """Check AI provider availability (lightweight test)"""
        start_time = time.time()
        
        try:
            from config import config
            
            active_provider = config.get('ACTIVE_AI_PROVIDER')
            ai_keys = config.get('AI_API_KEYS', {})
            
            if not active_provider:
                return HealthCheck(
                    name="ai_provider",
                    status=HealthStatus.UNHEALTHY,
                    response_time_ms=0,
                    message="No AI provider configured"
                )
            
            provider_key = ai_keys.get(active_provider)
            if not provider_key:
                return HealthCheck(
                    name="ai_provider",
                    status=HealthStatus.UNHEALTHY,
                    response_time_ms=0,
                    message=f"No API key for {active_provider}"
                )
            
            response_time = (time.time() - start_time) * 1000
            
            return HealthCheck(
                name="ai_provider",
                status=HealthStatus.HEALTHY,
                response_time_ms=response_time,
                message=f"AI provider {active_provider} configured",
                details={"provider": active_provider, "key_configured": bool(provider_key)}
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheck(
                name="ai_provider",
                status=HealthStatus.DEGRADED,
                response_time_ms=response_time,
                message=f"AI provider check failed: {str(e)[:100]}"
            )
    
    def _check_memory_health(self) -> HealthCheck:
        """Check system memory usage"""
        try:
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            if memory_percent < self.thresholds["memory_percent"]:
                status = HealthStatus.HEALTHY
                message = f"Memory usage normal ({memory_percent:.1f}%)"
            elif memory_percent < 95.0:
                status = HealthStatus.DEGRADED
                message = f"Memory usage high ({memory_percent:.1f}%)"
            else:
                status = HealthStatus.UNHEALTHY
                message = f"Memory usage critical ({memory_percent:.1f}%)"
            
            return HealthCheck(
                name="memory",
                status=status,
                response_time_ms=0,
                message=message,
                details={
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "percent_used": memory_percent
                }
            )
            
        except Exception as e:
            return HealthCheck(
                name="memory",
                status=HealthStatus.UNHEALTHY,
                response_time_ms=0,
                message=f"Memory check failed: {str(e)[:100]}"
            )
    
    def _check_disk_health(self) -> HealthCheck:
        """Check disk space usage"""
        try:
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            if disk_percent < self.thresholds["disk_percent"]:
                status = HealthStatus.HEALTHY
                message = f"Disk space sufficient ({disk_percent:.1f}% used)"
            elif disk_percent < 95.0:
                status = HealthStatus.DEGRADED
                message = f"Disk space low ({disk_percent:.1f}% used)"
            else:
                status = HealthStatus.UNHEALTHY
                message = f"Disk space critical ({disk_percent:.1f}% used)"
            
            return HealthCheck(
                name="disk",
                status=status,
                response_time_ms=0,
                message=message,
                details={
                    "total_gb": round(disk.total / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "percent_used": disk_percent
                }
            )
            
        except Exception as e:
            return HealthCheck(
                name="disk",
                status=HealthStatus.UNHEALTHY,
                response_time_ms=0,
                message=f"Disk check failed: {str(e)[:100]}"
            )
    
    async def _check_performance_health(self) -> HealthCheck:
        """Check system performance metrics"""
        try:
            from performance_monitor import performance_monitor
            
            metrics = performance_monitor.get_metrics_summary()
            avg_response_time = metrics.get("performance", {}).get("avg_response_time", 0) * 1000
            error_count = metrics.get("system", {}).get("total_errors", 0)
            total_commands = metrics.get("system", {}).get("total_commands", 1)
            error_rate = (error_count / total_commands) * 100 if total_commands > 0 else 0
            
            if avg_response_time < self.thresholds["response_time_ms"] and error_rate < self.thresholds["error_rate_percent"]:
                status = HealthStatus.HEALTHY
                message = f"Performance good (avg: {avg_response_time:.1f}ms, errors: {error_rate:.1f}%)"
            elif avg_response_time < self.thresholds["response_time_ms"] * 2 and error_rate < self.thresholds["error_rate_percent"] * 2:
                status = HealthStatus.DEGRADED
                message = f"Performance degraded (avg: {avg_response_time:.1f}ms, errors: {error_rate:.1f}%)"
            else:
                status = HealthStatus.UNHEALTHY
                message = f"Performance poor (avg: {avg_response_time:.1f}ms, errors: {error_rate:.1f}%)"
            
            return HealthCheck(
                name="performance",
                status=status,
                response_time_ms=avg_response_time,
                message=message,
                details={
                    "avg_response_time_ms": avg_response_time,
                    "error_rate_percent": error_rate,
                    "total_commands": total_commands,
                    "total_errors": error_count
                }
            )
            
        except Exception as e:
            return HealthCheck(
                name="performance",
                status=HealthStatus.DEGRADED,
                response_time_ms=0,
                message=f"Performance check failed: {str(e)[:100]}"
            )
    
    def _calculate_overall_status(self, health_checks: List[HealthCheck]) -> HealthStatus:
        """Calculate overall system health status"""
        if not health_checks:
            return HealthStatus.UNHEALTHY
        
        # Count status types
        status_counts = {status: 0 for status in HealthStatus}
        for check in health_checks:
            status_counts[check.status] += 1
        
        # Determine overall status
        if status_counts[HealthStatus.UNHEALTHY] > 0:
            return HealthStatus.UNHEALTHY
        elif status_counts[HealthStatus.DEGRADED] > 0:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.HEALTHY
    
    def _get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu_percent": round(cpu_percent, 1),
                "memory_percent": round(memory.percent, 1),
                "disk_percent": round((disk.used / disk.total) * 100, 1),
                "load_average": list(psutil.getloadavg()) if hasattr(psutil, 'getloadavg') else None,
                "boot_time": psutil.boot_time()
            }
        except Exception as e:
            logger.error(f"Failed to get system metrics: {e}")
            return {"error": "Failed to retrieve system metrics"}
    
    def _get_uptime(self) -> float:
        """Get system uptime in seconds"""
        try:
            return time.time() - psutil.boot_time()
        except:
            return 0.0
    
    async def get_simple_status(self) -> Dict[str, str]:
        """Get simple status for quick health checks"""
        try:
            # Quick checks without full health assessment
            from enhanced_db import enhanced_db
            
            # Test database with timeout
            db_result = enhanced_db.execute_query("SELECT 1", fetch='one')
            db_status = "ok" if db_result.success else "error"
            
            # Check memory
            memory_percent = psutil.virtual_memory().percent
            memory_status = "ok" if memory_percent < 90 else "warning"
            
            overall_status = "ok" if db_status == "ok" and memory_status == "ok" else "degraded"
            
            return {
                "status": overall_status,
                "database": db_status,
                "memory": memory_status,
                "timestamp": str(int(time.time()))
            }
            
        except Exception as e:
            logger.error(f"Simple status check failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": str(int(time.time()))
            }

# Global health monitor instance
health_monitor = HealthMonitor()