# src/config_manager.py
"""
Enhanced configuration management for Möbius AI Assistant.
Provides feature flags, environment-specific settings, and runtime configuration.
"""
import os
import json
import logging
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from pathlib import Path

logger = logging.getLogger(__name__)

class FeatureFlag(Enum):
    CONTEXTUAL_AI = "contextual_ai"
    PERFORMANCE_MONITORING = "performance_monitoring"
    SECURITY_AUDITING = "security_auditing"
    ENHANCED_UI = "enhanced_ui"
    ERROR_RECOVERY = "error_recovery"
    HEALTH_MONITORING = "health_monitoring"
    INPUT_VALIDATION = "input_validation"
    ADVANCED_CACHING = "advanced_caching"

@dataclass
class PerformanceConfig:
    max_concurrent_requests: int = 10
    database_pool_size: int = 10
    cache_ttl_seconds: int = 300
    response_timeout_seconds: int = 30
    max_retry_attempts: int = 3
    backoff_factor: float = 1.5

@dataclass
class SecurityConfig:
    audit_retention_days: int = 90
    max_failed_attempts: int = 5
    rate_limit_window_seconds: int = 60
    rate_limit_max_requests: int = 30
    suspicious_activity_threshold: int = 10
    enable_ip_tracking: bool = True

@dataclass
class UIConfig:
    enable_progress_indicators: bool = True
    enable_interactive_menus: bool = True
    enable_rich_formatting: bool = True
    max_suggestions: int = 5
    menu_timeout_seconds: int = 300

class EnhancedConfigManager:
    """
    Advanced configuration management with feature flags, environment-specific settings,
    and runtime configuration updates without compromising security or performance.
    """
    
    def __init__(self, config_dir: str = "data"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        self._lock = threading.RLock()
        self._config_cache = {}
        self._feature_flags = {}
        self._watchers = []
        
        # Configuration files
        self.main_config_file = self.config_dir / "enhanced_config.json"
        self.feature_flags_file = self.config_dir / "feature_flags.json"
        self.performance_config_file = self.config_dir / "performance_config.json"
        
        # Load configurations
        self._load_all_configs()
        
    def _load_all_configs(self):
        """Load all configuration files"""
        try:
            # Load main configuration
            self._config_cache = self._load_json_config(self.main_config_file, {})
            
            # Load feature flags
            self._feature_flags = self._load_json_config(self.feature_flags_file, self._get_default_feature_flags())
            
            # Load performance configuration
            perf_config = self._load_json_config(self.performance_config_file, {})
            self._config_cache["performance"] = PerformanceConfig(**perf_config) if perf_config else PerformanceConfig()
            
            # Load security configuration
            sec_config = self._config_cache.get("security", {})
            self._config_cache["security"] = SecurityConfig(**sec_config) if sec_config else SecurityConfig()
            
            # Load UI configuration
            ui_config = self._config_cache.get("ui", {})
            self._config_cache["ui"] = UIConfig(**ui_config) if ui_config else UIConfig()
            
            logger.info("Enhanced configuration loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load enhanced configuration: {e}")
            self._load_default_configs()
    
    def _load_json_config(self, file_path: Path, default: Dict[str, Any]) -> Dict[str, Any]:
        """Load JSON configuration file with fallback to default"""
        try:
            if file_path.exists():
                with open(file_path, 'r') as f:
                    return json.load(f)
            else:
                # Create default file
                with open(file_path, 'w') as f:
                    json.dump(default, f, indent=2)
                return default
        except Exception as e:
            logger.warning(f"Failed to load {file_path}: {e}, using defaults")
            return default
    
    def _get_default_feature_flags(self) -> Dict[str, bool]:
        """Get default feature flag settings"""
        return {
            FeatureFlag.CONTEXTUAL_AI.value: True,
            FeatureFlag.PERFORMANCE_MONITORING.value: True,
            FeatureFlag.SECURITY_AUDITING.value: True,
            FeatureFlag.ENHANCED_UI.value: True,
            FeatureFlag.ERROR_RECOVERY.value: True,
            FeatureFlag.HEALTH_MONITORING.value: True,
            FeatureFlag.INPUT_VALIDATION.value: True,
            FeatureFlag.ADVANCED_CACHING.value: True,
        }
    
    def _load_default_configs(self):
        """Load default configurations as fallback"""
        self._config_cache = {
            "performance": PerformanceConfig(),
            "security": SecurityConfig(),
            "ui": UIConfig()
        }
        self._feature_flags = self._get_default_feature_flags()
    
    def is_feature_enabled(self, feature: Union[FeatureFlag, str]) -> bool:
        """Check if a feature flag is enabled"""
        with self._lock:
            feature_name = feature.value if isinstance(feature, FeatureFlag) else feature
            return self._feature_flags.get(feature_name, False)
    
    def enable_feature(self, feature: Union[FeatureFlag, str], save: bool = True):
        """Enable a feature flag"""
        with self._lock:
            feature_name = feature.value if isinstance(feature, FeatureFlag) else feature
            self._feature_flags[feature_name] = True
            
            if save:
                self._save_feature_flags()
            
            logger.info(f"Feature enabled: {feature_name}")
    
    def disable_feature(self, feature: Union[FeatureFlag, str], save: bool = True):
        """Disable a feature flag"""
        with self._lock:
            feature_name = feature.value if isinstance(feature, FeatureFlag) else feature
            self._feature_flags[feature_name] = False
            
            if save:
                self._save_feature_flags()
            
            logger.info(f"Feature disabled: {feature_name}")
    
    def get_performance_config(self) -> PerformanceConfig:
        """Get performance configuration"""
        with self._lock:
            return self._config_cache.get("performance", PerformanceConfig())
    
    def update_performance_config(self, **kwargs):
        """Update performance configuration"""
        with self._lock:
            current_config = self.get_performance_config()
            
            # Update only provided fields
            for key, value in kwargs.items():
                if hasattr(current_config, key):
                    setattr(current_config, key, value)
            
            self._config_cache["performance"] = current_config
            self._save_performance_config()
            
            logger.info(f"Performance config updated: {kwargs}")
    
    def get_security_config(self) -> SecurityConfig:
        """Get security configuration"""
        with self._lock:
            return self._config_cache.get("security", SecurityConfig())
    
    def update_security_config(self, **kwargs):
        """Update security configuration"""
        with self._lock:
            current_config = self.get_security_config()
            
            # Update only provided fields
            for key, value in kwargs.items():
                if hasattr(current_config, key):
                    setattr(current_config, key, value)
            
            self._config_cache["security"] = current_config
            self._save_main_config()
            
            logger.info(f"Security config updated: {kwargs}")
    
    def get_ui_config(self) -> UIConfig:
        """Get UI configuration"""
        with self._lock:
            return self._config_cache.get("ui", UIConfig())
    
    def update_ui_config(self, **kwargs):
        """Update UI configuration"""
        with self._lock:
            current_config = self.get_ui_config()
            
            # Update only provided fields
            for key, value in kwargs.items():
                if hasattr(current_config, key):
                    setattr(current_config, key, value)
            
            self._config_cache["ui"] = current_config
            self._save_main_config()
            
            logger.info(f"UI config updated: {kwargs}")
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (supports dot notation)"""
        with self._lock:
            keys = key.split('.')
            value = self._config_cache
            
            for k in keys:
                if isinstance(value, dict):
                    value = value.get(k)
                elif hasattr(value, k):
                    value = getattr(value, k)
                else:
                    return default
                
                if value is None:
                    return default
            
            return value
    
    def set_config_value(self, key: str, value: Any, save: bool = True):
        """Set configuration value by key (supports dot notation)"""
        with self._lock:
            keys = key.split('.')
            config = self._config_cache
            
            # Navigate to the parent of the target key
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            
            # Set the value
            config[keys[-1]] = value
            
            if save:
                self._save_main_config()
            
            logger.info(f"Config value set: {key} = {value}")
    
    def get_all_feature_flags(self) -> Dict[str, bool]:
        """Get all feature flags"""
        with self._lock:
            return self._feature_flags.copy()
    
    def get_environment_info(self) -> Dict[str, Any]:
        """Get environment information for debugging"""
        return {
            "config_dir": str(self.config_dir),
            "config_files_exist": {
                "main_config": self.main_config_file.exists(),
                "feature_flags": self.feature_flags_file.exists(),
                "performance_config": self.performance_config_file.exists()
            },
            "feature_flags": self.get_all_feature_flags(),
            "performance_config": asdict(self.get_performance_config()),
            "security_config": asdict(self.get_security_config()),
            "ui_config": asdict(self.get_ui_config())
        }
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate current configuration and return issues"""
        issues = []
        warnings = []
        
        # Validate performance config
        perf_config = self.get_performance_config()
        if perf_config.max_concurrent_requests < 1:
            issues.append("max_concurrent_requests must be at least 1")
        if perf_config.database_pool_size < 1:
            issues.append("database_pool_size must be at least 1")
        if perf_config.cache_ttl_seconds < 0:
            issues.append("cache_ttl_seconds cannot be negative")
        
        # Validate security config
        sec_config = self.get_security_config()
        if sec_config.max_failed_attempts < 1:
            issues.append("max_failed_attempts must be at least 1")
        if sec_config.rate_limit_max_requests < 1:
            issues.append("rate_limit_max_requests must be at least 1")
        
        # Check for potential performance issues
        if perf_config.max_concurrent_requests > 50:
            warnings.append("High max_concurrent_requests may impact performance")
        if perf_config.database_pool_size > 20:
            warnings.append("Large database_pool_size may consume excessive memory")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }
    
    def reset_to_defaults(self, component: Optional[str] = None):
        """Reset configuration to defaults"""
        with self._lock:
            if component == "performance" or component is None:
                self._config_cache["performance"] = PerformanceConfig()
            
            if component == "security" or component is None:
                self._config_cache["security"] = SecurityConfig()
            
            if component == "ui" or component is None:
                self._config_cache["ui"] = UIConfig()
            
            if component == "features" or component is None:
                self._feature_flags = self._get_default_feature_flags()
            
            # Save all configurations
            self._save_all_configs()
            
            logger.info(f"Configuration reset to defaults: {component or 'all'}")
    
    def _save_feature_flags(self):
        """Save feature flags to file"""
        try:
            with open(self.feature_flags_file, 'w') as f:
                json.dump(self._feature_flags, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save feature flags: {e}")
    
    def _save_performance_config(self):
        """Save performance configuration to file"""
        try:
            perf_config = self.get_performance_config()
            with open(self.performance_config_file, 'w') as f:
                json.dump(asdict(perf_config), f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save performance config: {e}")
    
    def _save_main_config(self):
        """Save main configuration to file"""
        try:
            # Prepare config for saving (convert dataclasses to dicts)
            save_config = {}
            for key, value in self._config_cache.items():
                if hasattr(value, '__dict__'):
                    save_config[key] = asdict(value)
                else:
                    save_config[key] = value
            
            with open(self.main_config_file, 'w') as f:
                json.dump(save_config, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save main config: {e}")
    
    def _save_all_configs(self):
        """Save all configurations"""
        self._save_feature_flags()
        self._save_performance_config()
        self._save_main_config()

# Global enhanced config manager instance
enhanced_config = EnhancedConfigManager()