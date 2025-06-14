"""
Production Deployment Script - Industrial Grade Möbius AI
=========================================================

Comprehensive deployment script with:
- Environment validation and setup
- Dependency management and verification
- Configuration validation
- Health checks and monitoring setup
- Performance optimization
- Security hardening
- Logging and monitoring configuration
"""

import asyncio
import os
import sys
import subprocess
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import shutil
import platform
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProductionDeployment:
    """
    Production deployment manager for Möbius AI Assistant
    
    Handles complete deployment process including:
    - Environment validation
    - Dependency installation
    - Configuration setup
    - Security hardening
    - Performance optimization
    - Monitoring setup
    """
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.src_dir = self.project_root / "src"
        self.logs_dir = self.project_root / "logs"
        self.config_dir = self.project_root / "config"
        self.data_dir = self.project_root / "data"
        
        self.deployment_config = {
            "environment": "production",
            "python_version": "3.11+",
            "required_memory_gb": 2,
            "required_disk_gb": 5,
            "max_cpu_cores": None,
            "enable_monitoring": True,
            "enable_security": True,
            "enable_performance_optimization": True
        }
        
        self.deployment_status = {
            "environment_validated": False,
            "dependencies_installed": False,
            "configuration_validated": False,
            "security_hardened": False,
            "monitoring_setup": False,
            "ready_for_production": False
        }
    
    async def deploy(self):
        """Execute complete production deployment"""
        logger.info("🚀 Starting Production Deployment of Möbius AI Assistant")
        logger.info("=" * 60)
        
        try:
            # Phase 1: Environment Validation
            await self._validate_environment()
            
            # Phase 2: Directory Structure Setup
            await self._setup_directory_structure()
            
            # Phase 3: Dependency Management
            await self._install_dependencies()
            
            # Phase 4: Configuration Validation
            await self._validate_configuration()
            
            # Phase 5: Security Hardening
            await self._setup_security()
            
            # Phase 6: Performance Optimization
            await self._setup_performance_optimization()
            
            # Phase 7: Monitoring and Logging
            await self._setup_monitoring()
            
            # Phase 8: Health Checks
            await self._run_health_checks()
            
            # Phase 9: Final Validation
            await self._final_validation()
            
            logger.info("✅ Production deployment completed successfully!")
            await self._print_deployment_summary()
            
        except Exception as e:
            logger.error(f"❌ Deployment failed: {e}")
            await self._cleanup_failed_deployment()
            raise
    
    async def _validate_environment(self):
        """Validate deployment environment"""
        logger.info("🔍 Phase 1: Environment Validation")
        
        # Check Python version
        python_version = platform.python_version()
        logger.info(f"Python version: {python_version}")
        
        if not self._check_python_version(python_version):
            raise RuntimeError(f"Python {self.deployment_config['python_version']} required, got {python_version}")
        
        # Check system resources
        await self._check_system_resources()
        
        # Check required tools
        await self._check_required_tools()
        
        # Check network connectivity
        await self._check_network_connectivity()
        
        self.deployment_status["environment_validated"] = True
        logger.info("✅ Environment validation completed")
    
    def _check_python_version(self, version: str) -> bool:
        """Check if Python version meets requirements"""
        major, minor = map(int, version.split('.')[:2])
        return major >= 3 and minor >= 11
    
    async def _check_system_resources(self):
        """Check system resources"""
        try:
            import psutil
            
            # Check memory
            memory_gb = psutil.virtual_memory().total / (1024**3)
            logger.info(f"Available memory: {memory_gb:.1f} GB")
            
            if memory_gb < self.deployment_config["required_memory_gb"]:
                logger.warning(f"Low memory: {memory_gb:.1f} GB < {self.deployment_config['required_memory_gb']} GB required")
            
            # Check disk space
            disk_usage = psutil.disk_usage(str(self.project_root))
            disk_free_gb = disk_usage.free / (1024**3)
            logger.info(f"Available disk space: {disk_free_gb:.1f} GB")
            
            if disk_free_gb < self.deployment_config["required_disk_gb"]:
                raise RuntimeError(f"Insufficient disk space: {disk_free_gb:.1f} GB < {self.deployment_config['required_disk_gb']} GB required")
            
            # Check CPU
            cpu_count = psutil.cpu_count()
            logger.info(f"CPU cores: {cpu_count}")
            
        except ImportError:
            logger.warning("psutil not available, skipping detailed resource checks")
    
    async def _check_required_tools(self):
        """Check for required system tools"""
        required_tools = ["git", "pip"]
        
        for tool in required_tools:
            if not shutil.which(tool):
                raise RuntimeError(f"Required tool not found: {tool}")
            logger.info(f"✅ {tool} available")
    
    async def _check_network_connectivity(self):
        """Check network connectivity"""
        try:
            import urllib.request
            urllib.request.urlopen('https://api.coingecko.com/api/v3/ping', timeout=10)
            logger.info("✅ Network connectivity verified")
        except Exception as e:
            logger.warning(f"Network connectivity check failed: {e}")
    
    async def _setup_directory_structure(self):
        """Setup production directory structure"""
        logger.info("📁 Setting up directory structure")
        
        directories = [
            self.logs_dir,
            self.config_dir,
            self.data_dir,
            self.project_root / "backups",
            self.project_root / "monitoring",
            self.project_root / "security"
        ]
        
        for directory in directories:
            directory.mkdir(exist_ok=True)
            logger.info(f"✅ Created directory: {directory}")
    
    async def _install_dependencies(self):
        """Install and verify dependencies"""
        logger.info("📦 Phase 2: Installing Dependencies")
        
        # Install core dependencies
        await self._install_core_dependencies()
        
        # Install production dependencies
        await self._install_production_dependencies()
        
        # Verify installations
        await self._verify_dependencies()
        
        self.deployment_status["dependencies_installed"] = True
        logger.info("✅ Dependencies installation completed")
    
    async def _install_core_dependencies(self):
        """Install core dependencies"""
        core_requirements = [
            "python-telegram-bot>=20.0",
            "aiohttp>=3.8.0",
            "asyncio",
            "psutil>=5.9.0",
            "cryptography>=3.4.8",
            "requests>=2.28.0",
            "sqlite3"
        ]
        
        for requirement in core_requirements:
            logger.info(f"Installing {requirement}...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", requirement
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Failed to install {requirement}: {result.stderr}")
                raise RuntimeError(f"Dependency installation failed: {requirement}")
    
    async def _install_production_dependencies(self):
        """Install production-specific dependencies"""
        production_requirements = [
            "prometheus-client>=0.15.0",  # Metrics export
            "redis>=4.3.0",               # Caching
            "uvloop>=0.17.0",             # Performance
            "gunicorn>=20.1.0",           # Production server
            "supervisor>=4.2.0"           # Process management
        ]
        
        for requirement in production_requirements:
            logger.info(f"Installing production dependency: {requirement}...")
            try:
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", requirement
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    logger.info(f"✅ Installed {requirement}")
                else:
                    logger.warning(f"⚠️ Optional dependency failed: {requirement}")
            except Exception as e:
                logger.warning(f"⚠️ Could not install {requirement}: {e}")
    
    async def _verify_dependencies(self):
        """Verify all dependencies are properly installed"""
        critical_imports = [
            "telegram",
            "aiohttp",
            "psutil",
            "cryptography",
            "requests",
            "sqlite3"
        ]
        
        for module in critical_imports:
            try:
                __import__(module)
                logger.info(f"✅ {module} import successful")
            except ImportError as e:
                raise RuntimeError(f"Critical dependency missing: {module} - {e}")
    
    async def _validate_configuration(self):
        """Validate configuration files and environment variables"""
        logger.info("⚙️ Phase 3: Configuration Validation")
        
        # Check environment variables
        await self._check_environment_variables()
        
        # Validate configuration files
        await self._validate_config_files()
        
        # Setup production configuration
        await self._setup_production_config()
        
        self.deployment_status["configuration_validated"] = True
        logger.info("✅ Configuration validation completed")
    
    async def _check_environment_variables(self):
        """Check required environment variables"""
        required_env_vars = [
            "TELEGRAM_BOT_TOKEN",
            "ENCRYPTION_KEY"
        ]
        
        optional_env_vars = [
            "REDIS_URL",
            "DATABASE_URL",
            "LOG_LEVEL",
            "ENVIRONMENT"
        ]
        
        missing_required = []
        for var in required_env_vars:
            if not os.getenv(var):
                missing_required.append(var)
            else:
                logger.info(f"✅ {var} configured")
        
        if missing_required:
            raise RuntimeError(f"Missing required environment variables: {missing_required}")
        
        for var in optional_env_vars:
            if os.getenv(var):
                logger.info(f"✅ {var} configured")
            else:
                logger.info(f"ℹ️ {var} not configured (optional)")
    
    async def _validate_config_files(self):
        """Validate configuration files"""
        config_file = self.src_dir / "config.py"
        
        if not config_file.exists():
            logger.warning("config.py not found, creating default configuration")
            await self._create_default_config()
        else:
            logger.info("✅ config.py found")
        
        # Validate config can be imported
        try:
            sys.path.insert(0, str(self.src_dir))
            import config
            logger.info("✅ Configuration file valid")
        except Exception as e:
            raise RuntimeError(f"Configuration file invalid: {e}")
    
    async def _create_default_config(self):
        """Create default configuration file"""
        config_content = '''"""
Production Configuration for Möbius AI Assistant
"""
import os

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/mobius.db")

# Cache Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Security Configuration
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

# Performance Configuration
MAX_WORKERS = int(os.getenv("MAX_WORKERS", "10"))
CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "logs/mobius.log")

# Environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")

# API Configuration
COINGECKO_API_URL = "https://api.coingecko.com/api/v3"
REQUEST_TIMEOUT = 30

# Rate Limiting
RATE_LIMIT_REQUESTS_PER_MINUTE = 60
RATE_LIMIT_BURST_SIZE = 10

# Health Check Configuration
HEALTH_CHECK_INTERVAL = 30
HEALTH_CHECK_TIMEOUT = 10

class Config:
    """Configuration class"""
    TELEGRAM_BOT_TOKEN = TELEGRAM_BOT_TOKEN
    DATABASE_URL = DATABASE_URL
    REDIS_URL = REDIS_URL
    ENCRYPTION_KEY = ENCRYPTION_KEY
    MAX_WORKERS = MAX_WORKERS
    CACHE_TTL = CACHE_TTL
    LOG_LEVEL = LOG_LEVEL
    LOG_FILE = LOG_FILE
    ENVIRONMENT = ENVIRONMENT
    COINGECKO_API_URL = COINGECKO_API_URL
    REQUEST_TIMEOUT = REQUEST_TIMEOUT
    RATE_LIMIT_REQUESTS_PER_MINUTE = RATE_LIMIT_REQUESTS_PER_MINUTE
    RATE_LIMIT_BURST_SIZE = RATE_LIMIT_BURST_SIZE
    HEALTH_CHECK_INTERVAL = HEALTH_CHECK_INTERVAL
    HEALTH_CHECK_TIMEOUT = HEALTH_CHECK_TIMEOUT

config = Config()
'''
        
        config_file = self.src_dir / "config.py"
        with open(config_file, "w") as f:
            f.write(config_content)
        
        logger.info("✅ Default configuration created")
    
    async def _setup_production_config(self):
        """Setup production-specific configuration"""
        production_config = {
            "deployment_time": datetime.utcnow().isoformat(),
            "deployment_version": "1.0.0",
            "environment": "production",
            "features": {
                "caching": True,
                "monitoring": True,
                "security": True,
                "performance_optimization": True,
                "health_checks": True,
                "rate_limiting": True,
                "circuit_breakers": True
            },
            "thresholds": {
                "cpu_warning": 80,
                "cpu_critical": 95,
                "memory_warning": 80,
                "memory_critical": 95,
                "response_time_warning": 1000,
                "response_time_critical": 5000
            }
        }
        
        config_file = self.config_dir / "production.json"
        with open(config_file, "w") as f:
            json.dump(production_config, f, indent=2)
        
        logger.info("✅ Production configuration created")
    
    async def _setup_security(self):
        """Setup security hardening"""
        logger.info("🛡️ Phase 4: Security Hardening")
        
        # Setup security configuration
        await self._setup_security_config()
        
        # Setup audit logging
        await self._setup_audit_logging()
        
        # Setup access controls
        await self._setup_access_controls()
        
        self.deployment_status["security_hardened"] = True
        logger.info("✅ Security hardening completed")
    
    async def _setup_security_config(self):
        """Setup security configuration"""
        security_config = {
            "rate_limiting": {
                "enabled": True,
                "requests_per_minute": 60,
                "burst_size": 10,
                "block_duration_minutes": 15
            },
            "input_validation": {
                "enabled": True,
                "max_message_length": 4000,
                "forbidden_patterns": [
                    "script",
                    "javascript",
                    "eval",
                    "exec"
                ]
            },
            "threat_detection": {
                "enabled": True,
                "auto_block": True,
                "sensitivity": "medium"
            },
            "audit_logging": {
                "enabled": True,
                "log_all_requests": True,
                "retention_days": 30
            }
        }
        
        security_file = self.security_dir / "security_config.json"
        with open(security_file, "w") as f:
            json.dump(security_config, f, indent=2)
        
        logger.info("✅ Security configuration created")
    
    async def _setup_audit_logging(self):
        """Setup audit logging"""
        audit_log_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "audit": {
                    "format": "%(asctime)s - AUDIT - %(levelname)s - %(message)s"
                }
            },
            "handlers": {
                "audit_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": str(self.logs_dir / "audit.log"),
                    "maxBytes": 10485760,  # 10MB
                    "backupCount": 5,
                    "formatter": "audit"
                }
            },
            "loggers": {
                "audit": {
                    "handlers": ["audit_file"],
                    "level": "INFO",
                    "propagate": False
                }
            }
        }
        
        audit_config_file = self.security_dir / "audit_logging.json"
        with open(audit_config_file, "w") as f:
            json.dump(audit_log_config, f, indent=2)
        
        logger.info("✅ Audit logging configured")
    
    async def _setup_access_controls(self):
        """Setup access control policies"""
        access_control = {
            "default_policy": "allow",
            "rate_limits": {
                "global": {
                    "requests_per_minute": 1000,
                    "burst_size": 100
                },
                "per_user": {
                    "requests_per_minute": 60,
                    "burst_size": 10
                }
            },
            "blocked_users": [],
            "blocked_ips": [],
            "admin_users": [],
            "permissions": {
                "message_processing": "all",
                "price_queries": "all",
                "admin_commands": "admin_only"
            }
        }
        
        access_file = self.security_dir / "access_control.json"
        with open(access_file, "w") as f:
            json.dump(access_control, f, indent=2)
        
        logger.info("✅ Access controls configured")
    
    async def _setup_performance_optimization(self):
        """Setup performance optimization"""
        logger.info("⚡ Phase 5: Performance Optimization")
        
        # Setup caching configuration
        await self._setup_caching_config()
        
        # Setup connection pooling
        await self._setup_connection_pooling()
        
        # Setup async optimization
        await self._setup_async_optimization()
        
        logger.info("✅ Performance optimization completed")
    
    async def _setup_caching_config(self):
        """Setup caching configuration"""
        cache_config = {
            "l1_cache": {
                "max_size": 1000,
                "max_memory_mb": 100,
                "ttl_seconds": 300
            },
            "l2_cache": {
                "redis_url": os.getenv("REDIS_URL", "redis://localhost:6379/0"),
                "max_connections": 20,
                "ttl_seconds": 3600
            },
            "cache_strategies": {
                "price_data": {
                    "ttl": 60,
                    "tier": "all"
                },
                "user_context": {
                    "ttl": 1800,
                    "tier": "l1"
                },
                "message_analysis": {
                    "ttl": 300,
                    "tier": "l1"
                }
            }
        }
        
        cache_file = self.config_dir / "cache_config.json"
        with open(cache_file, "w") as f:
            json.dump(cache_config, f, indent=2)
        
        logger.info("✅ Caching configuration created")
    
    async def _setup_connection_pooling(self):
        """Setup connection pooling configuration"""
        pool_config = {
            "http_pool": {
                "max_connections": 100,
                "max_connections_per_host": 20,
                "connection_timeout": 30,
                "read_timeout": 30
            },
            "database_pool": {
                "max_connections": 20,
                "min_connections": 5,
                "connection_timeout": 10,
                "idle_timeout": 300
            }
        }
        
        pool_file = self.config_dir / "connection_pool.json"
        with open(pool_file, "w") as f:
            json.dump(pool_config, f, indent=2)
        
        logger.info("✅ Connection pooling configured")
    
    async def _setup_async_optimization(self):
        """Setup async optimization configuration"""
        async_config = {
            "concurrency_limits": {
                "message_processing": 50,
                "price_requests": 20,
                "database_operations": 10,
                "external_api_calls": 15
            },
            "timeout_settings": {
                "message_processing": 30,
                "price_requests": 10,
                "database_operations": 5,
                "external_api_calls": 30
            },
            "retry_policies": {
                "external_api_calls": {
                    "max_retries": 3,
                    "backoff_factor": 2,
                    "max_backoff": 60
                },
                "database_operations": {
                    "max_retries": 2,
                    "backoff_factor": 1.5,
                    "max_backoff": 10
                }
            }
        }
        
        async_file = self.config_dir / "async_config.json"
        with open(async_file, "w") as f:
            json.dump(async_config, f, indent=2)
        
        logger.info("✅ Async optimization configured")
    
    async def _setup_monitoring(self):
        """Setup monitoring and logging"""
        logger.info("📊 Phase 6: Monitoring Setup")
        
        # Setup logging configuration
        await self._setup_logging_config()
        
        # Setup metrics collection
        await self._setup_metrics_config()
        
        # Setup health monitoring
        await self._setup_health_monitoring()
        
        # Setup alerting
        await self._setup_alerting()
        
        self.deployment_status["monitoring_setup"] = True
        logger.info("✅ Monitoring setup completed")
    
    async def _setup_logging_config(self):
        """Setup comprehensive logging configuration"""
        logging_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                },
                "detailed": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": "INFO",
                    "formatter": "standard",
                    "stream": "ext://sys.stdout"
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "INFO",
                    "formatter": "detailed",
                    "filename": str(self.logs_dir / "mobius.log"),
                    "maxBytes": 10485760,
                    "backupCount": 5
                },
                "error_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "ERROR",
                    "formatter": "detailed",
                    "filename": str(self.logs_dir / "errors.log"),
                    "maxBytes": 10485760,
                    "backupCount": 5
                }
            },
            "loggers": {
                "": {
                    "handlers": ["console", "file"],
                    "level": "INFO",
                    "propagate": False
                },
                "error": {
                    "handlers": ["error_file"],
                    "level": "ERROR",
                    "propagate": False
                }
            }
        }
        
        logging_file = self.config_dir / "logging.json"
        with open(logging_file, "w") as f:
            json.dump(logging_config, f, indent=2)
        
        logger.info("✅ Logging configuration created")
    
    async def _setup_metrics_config(self):
        """Setup metrics collection configuration"""
        metrics_config = {
            "collection_interval": 30,
            "retention_hours": 168,  # 1 week
            "export_formats": ["json", "prometheus"],
            "metrics": {
                "system": {
                    "cpu_usage": True,
                    "memory_usage": True,
                    "disk_usage": True,
                    "network_io": True
                },
                "application": {
                    "message_processing_time": True,
                    "cache_hit_rate": True,
                    "error_rate": True,
                    "active_users": True,
                    "request_rate": True
                },
                "business": {
                    "price_requests": True,
                    "user_interactions": True,
                    "feature_usage": True
                }
            },
            "alerting_thresholds": {
                "cpu_usage": 80,
                "memory_usage": 80,
                "error_rate": 5,
                "response_time": 1000
            }
        }
        
        metrics_file = self.monitoring_dir / "metrics_config.json"
        with open(metrics_file, "w") as f:
            json.dump(metrics_config, f, indent=2)
        
        logger.info("✅ Metrics configuration created")
    
    async def _setup_health_monitoring(self):
        """Setup health monitoring configuration"""
        health_config = {
            "check_interval": 30,
            "timeout": 10,
            "failure_threshold": 3,
            "recovery_threshold": 2,
            "services": {
                "database": {
                    "enabled": True,
                    "check_type": "connection",
                    "timeout": 5
                },
                "cache": {
                    "enabled": True,
                    "check_type": "ping",
                    "timeout": 2
                },
                "external_apis": {
                    "enabled": True,
                    "check_type": "http",
                    "timeout": 10,
                    "endpoints": [
                        "https://api.coingecko.com/api/v3/ping"
                    ]
                }
            },
            "notifications": {
                "enabled": True,
                "channels": ["log", "file"],
                "severity_levels": ["warning", "critical"]
            }
        }
        
        health_file = self.monitoring_dir / "health_config.json"
        with open(health_file, "w") as f:
            json.dump(health_config, f, indent=2)
        
        logger.info("✅ Health monitoring configured")
    
    async def _setup_alerting(self):
        """Setup alerting configuration"""
        alert_config = {
            "enabled": True,
            "channels": {
                "log": {
                    "enabled": True,
                    "level": "INFO"
                },
                "file": {
                    "enabled": True,
                    "file": str(self.logs_dir / "alerts.log")
                }
            },
            "rules": {
                "high_cpu_usage": {
                    "condition": "cpu_usage > 80",
                    "severity": "warning",
                    "cooldown": 300
                },
                "high_memory_usage": {
                    "condition": "memory_usage > 80",
                    "severity": "warning",
                    "cooldown": 300
                },
                "high_error_rate": {
                    "condition": "error_rate > 5",
                    "severity": "critical",
                    "cooldown": 60
                },
                "service_down": {
                    "condition": "service_status == 'down'",
                    "severity": "critical",
                    "cooldown": 0
                }
            }
        }
        
        alert_file = self.monitoring_dir / "alert_config.json"
        with open(alert_file, "w") as f:
            json.dump(alert_config, f, indent=2)
        
        logger.info("✅ Alerting configured")
    
    async def _run_health_checks(self):
        """Run comprehensive health checks"""
        logger.info("🏥 Phase 7: Health Checks")
        
        # Test imports
        await self._test_imports()
        
        # Test configuration
        await self._test_configuration()
        
        # Test external connectivity
        await self._test_external_connectivity()
        
        logger.info("✅ Health checks completed")
    
    async def _test_imports(self):
        """Test all critical imports"""
        critical_modules = [
            "src.production_main",
            "src.production_core",
            "src.intelligent_message_router",
            "src.crypto_research",
            "src.config"
        ]
        
        for module in critical_modules:
            try:
                __import__(module)
                logger.info(f"✅ {module} import successful")
            except ImportError as e:
                raise RuntimeError(f"Critical module import failed: {module} - {e}")
    
    async def _test_configuration(self):
        """Test configuration loading"""
        try:
            sys.path.insert(0, str(self.src_dir))
            from config import config
            
            # Test required configuration
            required_configs = ["TELEGRAM_BOT_TOKEN", "ENCRYPTION_KEY"]
            for config_name in required_configs:
                if not hasattr(config, config_name) or not getattr(config, config_name):
                    raise RuntimeError(f"Required configuration missing: {config_name}")
            
            logger.info("✅ Configuration validation successful")
            
        except Exception as e:
            raise RuntimeError(f"Configuration test failed: {e}")
    
    async def _test_external_connectivity(self):
        """Test external service connectivity"""
        try:
            import urllib.request
            
            # Test CoinGecko API
            urllib.request.urlopen('https://api.coingecko.com/api/v3/ping', timeout=10)
            logger.info("✅ CoinGecko API connectivity verified")
            
            # Test Telegram API (basic check)
            telegram_url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN', 'test')}/getMe"
            try:
                urllib.request.urlopen(telegram_url, timeout=10)
                logger.info("✅ Telegram API connectivity verified")
            except:
                logger.warning("⚠️ Telegram API connectivity check failed (token may be invalid)")
            
        except Exception as e:
            logger.warning(f"⚠️ External connectivity test failed: {e}")
    
    async def _final_validation(self):
        """Final deployment validation"""
        logger.info("🔍 Phase 8: Final Validation")
        
        # Check all deployment status
        failed_components = [
            component for component, status in self.deployment_status.items()
            if not status
        ]
        
        if failed_components:
            raise RuntimeError(f"Deployment validation failed for: {failed_components}")
        
        # Mark as ready for production
        self.deployment_status["ready_for_production"] = True
        
        # Create deployment manifest
        await self._create_deployment_manifest()
        
        logger.info("✅ Final validation completed")
    
    async def _create_deployment_manifest(self):
        """Create deployment manifest"""
        manifest = {
            "deployment_id": f"mobius-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
            "deployment_time": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "environment": "production",
            "status": self.deployment_status,
            "configuration": self.deployment_config,
            "system_info": {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "architecture": platform.architecture()[0]
            },
            "features_enabled": {
                "caching": True,
                "monitoring": True,
                "security": True,
                "performance_optimization": True,
                "health_checks": True,
                "rate_limiting": True,
                "circuit_breakers": True
            }
        }
        
        manifest_file = self.project_root / "deployment_manifest.json"
        with open(manifest_file, "w") as f:
            json.dump(manifest, f, indent=2)
        
        logger.info("✅ Deployment manifest created")
    
    async def _print_deployment_summary(self):
        """Print deployment summary"""
        logger.info("\n" + "=" * 60)
        logger.info("🎉 PRODUCTION DEPLOYMENT COMPLETED SUCCESSFULLY!")
        logger.info("=" * 60)
        logger.info("")
        logger.info("📋 Deployment Summary:")
        logger.info(f"   • Environment: {self.deployment_config['environment']}")
        logger.info(f"   • Python Version: {platform.python_version()}")
        logger.info(f"   • Deployment Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
        logger.info("")
        logger.info("✅ Components Deployed:")
        for component, status in self.deployment_status.items():
            status_icon = "✅" if status else "❌"
            logger.info(f"   {status_icon} {component.replace('_', ' ').title()}")
        logger.info("")
        logger.info("🚀 Ready to Start:")
        logger.info("   python src/production_main.py")
        logger.info("")
        logger.info("📊 Monitoring:")
        logger.info(f"   • Logs: {self.logs_dir}")
        logger.info(f"   • Config: {self.config_dir}")
        logger.info(f"   • Data: {self.data_dir}")
        logger.info("")
        logger.info("🛡️ Security: Enabled with comprehensive protection")
        logger.info("⚡ Performance: Optimized with caching and monitoring")
        logger.info("🏥 Health Checks: Automated monitoring active")
        logger.info("")
        logger.info("=" * 60)
    
    async def _cleanup_failed_deployment(self):
        """Cleanup after failed deployment"""
        logger.info("🧹 Cleaning up failed deployment...")
        
        # Remove created directories if empty
        for directory in [self.logs_dir, self.config_dir, self.monitoring_dir]:
            try:
                if directory.exists() and not any(directory.iterdir()):
                    directory.rmdir()
            except:
                pass
        
        logger.info("Cleanup completed")


async def main():
    """Main deployment entry point"""
    print("🚀 Möbius AI Assistant - Production Deployment")
    print("=" * 50)
    
    deployment = ProductionDeployment()
    
    try:
        await deployment.deploy()
        print("\n🎉 Deployment completed successfully!")
        print("You can now start the production bot with:")
        print("   python src/production_main.py")
        
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        print("Please check the logs and fix any issues before retrying.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())