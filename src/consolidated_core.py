#!/usr/bin/env python3
"""
CONSOLIDATED CORE SYSTEM
========================
Unified core system consolidating multiple modules for better maintainability and security.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

# Import consolidated modules
from secure_database_manager import secure_db_manager, init_secure_database
from secure_redis_cache import secure_cache, init_cache
from enhanced_monitoring import metrics_collector, start_monitoring, record_metric, increment_counter

logger = logging.getLogger(__name__)

@dataclass
class CoreConfig:
    """Unified configuration for core systems"""
    database_enabled: bool = True
    cache_enabled: bool = True
    monitoring_enabled: bool = True
    security_hardening: bool = True
    performance_optimization: bool = True
    auto_scaling: bool = False

class ConsolidatedCore:
    """Unified core system manager"""
    
    def __init__(self, config: CoreConfig):
        self.config = config
        self.initialized = False
        self.startup_time = None
        self.health_status = "UNKNOWN"
        
        # Component status tracking
        self.components = {
            'database': {'status': 'STOPPED', 'last_check': None},
            'cache': {'status': 'STOPPED', 'last_check': None},
            'monitoring': {'status': 'STOPPED', 'last_check': None}
        }
    
    async def initialize(self) -> bool:
        """Initialize all core systems with proper error handling"""
        logger.info("🚀 Initializing Consolidated Core System...")
        self.startup_time = time.time()
        
        try:
            # Initialize database
            if self.config.database_enabled:
                logger.info("📊 Initializing secure database...")
                db_success = await self._init_database()
                self.components['database']['status'] = 'RUNNING' if db_success else 'FAILED'
                self.components['database']['last_check'] = time.time()
                
                if not db_success:
                    logger.error("❌ Database initialization failed")
                    return False
            
            # Initialize cache
            if self.config.cache_enabled:
                logger.info("🗄️ Initializing secure cache...")
                cache_success = await self._init_cache()
                self.components['cache']['status'] = 'RUNNING' if cache_success else 'FAILED'
                self.components['cache']['last_check'] = time.time()
                
                if not cache_success:
                    logger.warning("⚠️ Cache initialization failed, continuing without cache")
            
            # Initialize monitoring
            if self.config.monitoring_enabled:
                logger.info("📈 Initializing monitoring system...")
                monitoring_success = await self._init_monitoring()
                self.components['monitoring']['status'] = 'RUNNING' if monitoring_success else 'FAILED'
                self.components['monitoring']['last_check'] = time.time()
            
            # Perform health check
            await self._initial_health_check()
            
            self.initialized = True
            startup_duration = time.time() - self.startup_time
            
            logger.info(f"✅ Consolidated Core System initialized successfully in {startup_duration:.2f}s")
            
            # Record startup metrics
            record_metric("core.startup_time", startup_duration)
            increment_counter("core.initializations")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Core system initialization failed: {e}")
            self.health_status = "CRITICAL"
            return False
    
    async def _init_database(self) -> bool:
        """Initialize database with error handling"""
        try:
            await init_secure_database()
            
            # Test database connection
            test_result = await secure_db_manager.get_stats()
            if test_result:
                logger.info("✅ Database connection verified")
                return True
            else:
                logger.error("❌ Database connection test failed")
                return False
                
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            return False
    
    async def _init_cache(self) -> bool:
        """Initialize cache with error handling"""
        try:
            cache_success = await init_cache()
            
            if cache_success:
                # Test cache operations
                test_success = await secure_cache.health_check()
                if test_success:
                    logger.info("✅ Cache connection verified")
                    return True
                else:
                    logger.error("❌ Cache health check failed")
                    return False
            else:
                return False
                
        except Exception as e:
            logger.error(f"Cache initialization error: {e}")
            return False
    
    async def _init_monitoring(self) -> bool:
        """Initialize monitoring with error handling"""
        try:
            await start_monitoring()
            logger.info("✅ Monitoring system started")
            return True
        except Exception as e:
            logger.error(f"Monitoring initialization error: {e}")
            return False
    
    async def _initial_health_check(self):
        """Perform initial health check"""
        try:
            health_data = await self.get_health_status()
            self.health_status = health_data['status']
            logger.info(f"🏥 Initial health check: {self.health_status}")
        except Exception as e:
            logger.error(f"Initial health check failed: {e}")
            self.health_status = "UNKNOWN"
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status"""
        try:
            health_data = {
                'overall_status': 'HEALTHY',
                'components': {},
                'metrics': {},
                'timestamp': time.time(),
                'uptime': time.time() - self.startup_time if self.startup_time else 0
            }
            
            # Check each component
            for component_name, component_info in self.components.items():
                component_health = await self._check_component_health(component_name)
                health_data['components'][component_name] = component_health
                
                # Update overall status based on component health
                if component_health['status'] == 'FAILED':
                    if component_name == 'database':
                        health_data['overall_status'] = 'CRITICAL'
                    elif health_data['overall_status'] == 'HEALTHY':
                        health_data['overall_status'] = 'DEGRADED'
            
            # Get system metrics if monitoring is available
            if self.components['monitoring']['status'] == 'RUNNING':
                try:
                    from enhanced_monitoring import metrics_collector
                    system_health = metrics_collector.get_health_status()
                    health_data['metrics'] = system_health
                except Exception as e:
                    logger.error(f"Error getting system metrics: {e}")
            
            return health_data
            
        except Exception as e:
            logger.error(f"Error getting health status: {e}")
            return {
                'overall_status': 'UNKNOWN',
                'error': str(e),
                'timestamp': time.time()
            }
    
    async def _check_component_health(self, component_name: str) -> Dict[str, Any]:
        """Check health of individual component"""
        component_info = self.components[component_name]
        
        try:
            if component_name == 'database':
                if self.config.database_enabled:
                    stats = await secure_db_manager.get_stats()
                    return {
                        'status': 'RUNNING' if stats else 'FAILED',
                        'details': stats,
                        'last_check': time.time()
                    }
                else:
                    return {'status': 'DISABLED', 'last_check': time.time()}
            
            elif component_name == 'cache':
                if self.config.cache_enabled:
                    health_ok = await secure_cache.health_check()
                    cache_stats = await secure_cache.get_cache_stats()
                    return {
                        'status': 'RUNNING' if health_ok else 'FAILED',
                        'details': cache_stats,
                        'last_check': time.time()
                    }
                else:
                    return {'status': 'DISABLED', 'last_check': time.time()}
            
            elif component_name == 'monitoring':
                if self.config.monitoring_enabled:
                    # Monitoring is healthy if it's collecting metrics
                    return {
                        'status': 'RUNNING' if metrics_collector.is_collecting else 'FAILED',
                        'details': {'collecting': metrics_collector.is_collecting},
                        'last_check': time.time()
                    }
                else:
                    return {'status': 'DISABLED', 'last_check': time.time()}
            
            else:
                return {'status': 'UNKNOWN', 'last_check': time.time()}
                
        except Exception as e:
            logger.error(f"Error checking {component_name} health: {e}")
            return {
                'status': 'FAILED',
                'error': str(e),
                'last_check': time.time()
            }
    
    async def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        try:
            stats = {
                'core': {
                    'uptime': time.time() - self.startup_time if self.startup_time else 0,
                    'initialized': self.initialized,
                    'health_status': self.health_status
                },
                'database': {},
                'cache': {},
                'monitoring': {}
            }
            
            # Database stats
            if self.components['database']['status'] == 'RUNNING':
                try:
                    db_stats = await secure_db_manager.get_stats()
                    stats['database'] = db_stats
                except Exception as e:
                    stats['database'] = {'error': str(e)}
            
            # Cache stats
            if self.components['cache']['status'] == 'RUNNING':
                try:
                    cache_stats = await secure_cache.get_cache_stats()
                    stats['cache'] = cache_stats
                except Exception as e:
                    stats['cache'] = {'error': str(e)}
            
            # Monitoring stats
            if self.components['monitoring']['status'] == 'RUNNING':
                try:
                    monitoring_stats = metrics_collector.get_metrics_summary()
                    stats['monitoring'] = monitoring_stats
                except Exception as e:
                    stats['monitoring'] = {'error': str(e)}
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting performance stats: {e}")
            return {'error': str(e)}
    
    async def restart_component(self, component_name: str) -> bool:
        """Restart a specific component"""
        logger.info(f"🔄 Restarting component: {component_name}")
        
        try:
            if component_name == 'database':
                await secure_db_manager.cleanup()
                success = await self._init_database()
                
            elif component_name == 'cache':
                await secure_cache.cleanup()
                success = await self._init_cache()
                
            elif component_name == 'monitoring':
                await metrics_collector.stop_collection()
                success = await self._init_monitoring()
                
            else:
                logger.error(f"Unknown component: {component_name}")
                return False
            
            if success:
                self.components[component_name]['status'] = 'RUNNING'
                self.components[component_name]['last_check'] = time.time()
                logger.info(f"✅ Component {component_name} restarted successfully")
                
                # Record restart metric
                increment_counter(f"core.{component_name}.restarts")
                
            else:
                self.components[component_name]['status'] = 'FAILED'
                logger.error(f"❌ Component {component_name} restart failed")
            
            return success
            
        except Exception as e:
            logger.error(f"Error restarting component {component_name}: {e}")
            self.components[component_name]['status'] = 'FAILED'
            return False
    
    async def shutdown(self):
        """Gracefully shutdown all core systems"""
        logger.info("🛑 Shutting down Consolidated Core System...")
        
        try:
            # Stop monitoring first
            if self.components['monitoring']['status'] == 'RUNNING':
                await metrics_collector.stop_collection()
                self.components['monitoring']['status'] = 'STOPPED'
            
            # Cleanup cache
            if self.components['cache']['status'] == 'RUNNING':
                await secure_cache.cleanup()
                self.components['cache']['status'] = 'STOPPED'
            
            # Cleanup database
            if self.components['database']['status'] == 'RUNNING':
                await secure_db_manager.cleanup()
                self.components['database']['status'] = 'STOPPED'
            
            self.initialized = False
            self.health_status = "STOPPED"
            
            logger.info("✅ Consolidated Core System shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

# Performance optimization utilities
class PerformanceOptimizer:
    """Performance optimization utilities"""
    
    @staticmethod
    async def optimize_database_queries():
        """Optimize database query performance"""
        try:
            # Analyze slow queries and suggest optimizations
            if secure_db_manager.pool:
                stats = await secure_db_manager.get_stats()
                pool_stats = stats.get('pool_stats', {})
                avg_query_time = pool_stats.get('query_stats', {}).get('avg_query_time', 0)
                
                if avg_query_time > 1.0:  # Queries taking more than 1 second
                    logger.warning(f"Slow queries detected: avg {avg_query_time:.2f}s")
                    # Could implement query optimization suggestions here
                
                return {
                    'avg_query_time': avg_query_time,
                    'optimization_needed': avg_query_time > 1.0
                }
        except Exception as e:
            logger.error(f"Database optimization check failed: {e}")
            return {'error': str(e)}
    
    @staticmethod
    async def optimize_cache_performance():
        """Optimize cache performance"""
        try:
            if secure_cache.redis:
                cache_stats = await secure_cache.get_cache_stats()
                hit_ratio = cache_stats.get('hit_ratio', 0)
                
                if hit_ratio < 0.8:  # Less than 80% hit ratio
                    logger.warning(f"Low cache hit ratio: {hit_ratio:.2f}")
                    # Could implement cache optimization suggestions here
                
                return {
                    'hit_ratio': hit_ratio,
                    'optimization_needed': hit_ratio < 0.8
                }
        except Exception as e:
            logger.error(f"Cache optimization check failed: {e}")
            return {'error': str(e)}

# Global core instance
core_config = CoreConfig()
consolidated_core = ConsolidatedCore(core_config)

# Convenience functions
async def init_core_system(config: Optional[CoreConfig] = None) -> bool:
    """Initialize the consolidated core system"""
    global consolidated_core
    if config:
        consolidated_core = ConsolidatedCore(config)
    return await consolidated_core.initialize()

async def get_core_health() -> Dict[str, Any]:
    """Get core system health"""
    return await consolidated_core.get_health_status()

async def get_core_stats() -> Dict[str, Any]:
    """Get core system performance stats"""
    return await consolidated_core.get_performance_stats()

async def restart_core_component(component_name: str) -> bool:
    """Restart a core component"""
    return await consolidated_core.restart_component(component_name)

async def shutdown_core_system():
    """Shutdown the core system"""
    await consolidated_core.shutdown()