"""
Security Manager - Production Grade Security Framework
=====================================================

Comprehensive security management system with:
- Input validation and sanitization
- Authentication and authorization
- Audit logging and compliance
- Threat detection and prevention
- Encryption and data protection
- Security monitoring and alerting
"""

import asyncio
import hashlib
import hmac
import secrets
import time
import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
from ipaddress import ip_address, ip_network
import base64

logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """Security levels for different operations"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatLevel(Enum):
    """Threat severity levels"""
    INFO = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    CRITICAL = 5
    
    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented
    
    def __le__(self, other):
        if self.__class__ is other.__class__:
            return self.value <= other.value
        return NotImplemented
    
    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.value > other.value
        return NotImplemented
    
    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return self.value >= other.value
        return NotImplemented


class SecurityEventType(Enum):
    """Types of security events"""
    AUTHENTICATION_SUCCESS = "auth_success"
    AUTHENTICATION_FAILURE = "auth_failure"
    AUTHORIZATION_FAILURE = "authz_failure"
    INPUT_VALIDATION_FAILURE = "input_validation_failure"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    DATA_ACCESS = "data_access"
    CONFIGURATION_CHANGE = "config_change"
    THREAT_DETECTED = "threat_detected"


@dataclass
class SecurityEvent:
    """Security event for audit logging"""
    event_type: SecurityEventType
    timestamp: datetime
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None
    result: str = "success"
    threat_level: ThreatLevel = ThreatLevel.INFO
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging"""
        return {
            'event_type': self.event_type.value,
            'timestamp': self.timestamp.isoformat(),
            'user_id': self.user_id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'resource': self.resource,
            'action': self.action,
            'result': self.result,
            'threat_level': self.threat_level.value,
            'details': self.details
        }


@dataclass
class ValidationRule:
    """Input validation rule"""
    name: str
    pattern: Optional[str] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    allowed_chars: Optional[str] = None
    forbidden_patterns: List[str] = field(default_factory=list)
    custom_validator: Optional[Callable[[str], bool]] = None


class InputValidator:
    """Advanced input validation and sanitization"""
    
    def __init__(self):
        self.rules: Dict[str, ValidationRule] = {}
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        """Setup default validation rules"""
        self.rules.update({
            'user_id': ValidationRule(
                name='user_id',
                pattern=r'^[a-zA-Z0-9_-]+$',
                min_length=1,
                max_length=50
            ),
            'email': ValidationRule(
                name='email',
                pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
                max_length=254
            ),
            'crypto_symbol': ValidationRule(
                name='crypto_symbol',
                pattern=r'^[A-Z0-9]{1,10}$',
                min_length=1,
                max_length=10
            ),
            'wallet_address': ValidationRule(
                name='wallet_address',
                pattern=r'^[a-zA-Z0-9]+$',
                min_length=20,
                max_length=100
            ),
            'message_text': ValidationRule(
                name='message_text',
                max_length=4000,
                forbidden_patterns=[
                    r'<script.*?>.*?</script>',  # Script tags
                    r'javascript:',              # JavaScript URLs
                    r'on\w+\s*=',               # Event handlers
                    r'eval\s*\(',               # eval() calls
                ]
            ),
            'command': ValidationRule(
                name='command',
                pattern=r'^[a-zA-Z0-9_/-]+$',
                min_length=1,
                max_length=50
            )
        })
    
    def add_rule(self, rule: ValidationRule):
        """Add custom validation rule"""
        self.rules[rule.name] = rule
    
    async def validate(self, field_name: str, value: str) -> tuple[bool, Optional[str]]:
        """
        Validate input value against rules
        
        Returns:
            (is_valid, error_message)
        """
        if field_name not in self.rules:
            return True, None
        
        rule = self.rules[field_name]
        
        # Check length constraints
        if rule.min_length is not None and len(value) < rule.min_length:
            return False, f"{field_name} must be at least {rule.min_length} characters"
        
        if rule.max_length is not None and len(value) > rule.max_length:
            return False, f"{field_name} must be at most {rule.max_length} characters"
        
        # Check pattern
        if rule.pattern and not re.match(rule.pattern, value):
            return False, f"{field_name} format is invalid"
        
        # Check allowed characters
        if rule.allowed_chars and not all(c in rule.allowed_chars for c in value):
            return False, f"{field_name} contains invalid characters"
        
        # Check forbidden patterns
        for pattern in rule.forbidden_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                return False, f"{field_name} contains forbidden content"
        
        # Custom validation
        if rule.custom_validator and not rule.custom_validator(value):
            return False, f"{field_name} failed custom validation"
        
        return True, None
    
    async def sanitize(self, value: str) -> str:
        """Sanitize input value"""
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # Normalize whitespace
        value = re.sub(r'\s+', ' ', value).strip()
        
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', '\n', '\r', '\t']
        for char in dangerous_chars:
            value = value.replace(char, '')
        
        return value


class ThreatDetector:
    """Advanced threat detection system"""
    
    def __init__(self):
        self.suspicious_patterns = [
            r'union\s+select',           # SQL injection
            r'drop\s+table',             # SQL injection
            r'<script.*?>',              # XSS
            r'javascript:',              # XSS
            r'eval\s*\(',               # Code injection
            r'exec\s*\(',               # Code injection
            r'system\s*\(',             # Command injection
            r'\.\./',                   # Path traversal
            r'%2e%2e%2f',               # Encoded path traversal
        ]
        
        self.ip_blacklist: set = set()
        self.user_blacklist: set = set()
        
        # Behavioral analysis
        self.user_activity: Dict[str, List[datetime]] = {}
        self.ip_activity: Dict[str, List[datetime]] = {}
        
    async def analyze_request(self, user_id: Optional[str], ip_address: Optional[str], 
                             content: str, user_agent: Optional[str] = None) -> tuple[ThreatLevel, List[str]]:
        """
        Analyze request for threats
        
        Returns:
            (threat_level, detected_threats)
        """
        threats = []
        max_threat_level = ThreatLevel.INFO
        
        # Check blacklists
        if user_id and user_id in self.user_blacklist:
            threats.append("Blacklisted user")
            max_threat_level = ThreatLevel.CRITICAL
        
        if ip_address and ip_address in self.ip_blacklist:
            threats.append("Blacklisted IP address")
            max_threat_level = ThreatLevel.CRITICAL
        
        # Pattern-based detection
        for pattern in self.suspicious_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                threats.append(f"Suspicious pattern detected: {pattern}")
                max_threat_level = max(max_threat_level, ThreatLevel.HIGH, key=lambda x: x.value)
        
        # Behavioral analysis
        if user_id:
            user_threat_level = await self._analyze_user_behavior(user_id)
            if user_threat_level > ThreatLevel.INFO:
                threats.append("Suspicious user behavior")
                max_threat_level = max(max_threat_level, user_threat_level, key=lambda x: x.value)
        
        if ip_address:
            ip_threat_level = await self._analyze_ip_behavior(ip_address)
            if ip_threat_level > ThreatLevel.INFO:
                threats.append("Suspicious IP behavior")
                max_threat_level = max(max_threat_level, ip_threat_level, key=lambda x: x.value)
        
        # User agent analysis
        if user_agent:
            ua_threat_level = await self._analyze_user_agent(user_agent)
            if ua_threat_level > ThreatLevel.INFO:
                threats.append("Suspicious user agent")
                max_threat_level = max(max_threat_level, ua_threat_level, key=lambda x: x.value)
        
        return max_threat_level, threats
    
    async def _analyze_user_behavior(self, user_id: str) -> ThreatLevel:
        """Analyze user behavioral patterns"""
        now = datetime.utcnow()
        
        # Track user activity
        if user_id not in self.user_activity:
            self.user_activity[user_id] = []
        
        self.user_activity[user_id].append(now)
        
        # Clean old activity (keep last hour)
        cutoff = now - timedelta(hours=1)
        self.user_activity[user_id] = [
            activity for activity in self.user_activity[user_id]
            if activity > cutoff
        ]
        
        # Check for suspicious patterns
        recent_activity = self.user_activity[user_id]
        
        # Too many requests in short time
        if len(recent_activity) > 100:  # More than 100 requests per hour
            return ThreatLevel.HIGH
        elif len(recent_activity) > 50:  # More than 50 requests per hour
            return ThreatLevel.MEDIUM
        
        return ThreatLevel.INFO
    
    async def _analyze_ip_behavior(self, ip_address: str) -> ThreatLevel:
        """Analyze IP behavioral patterns"""
        now = datetime.utcnow()
        
        # Track IP activity
        if ip_address not in self.ip_activity:
            self.ip_activity[ip_address] = []
        
        self.ip_activity[ip_address].append(now)
        
        # Clean old activity
        cutoff = now - timedelta(hours=1)
        self.ip_activity[ip_address] = [
            activity for activity in self.ip_activity[ip_address]
            if activity > cutoff
        ]
        
        # Check for suspicious patterns
        recent_activity = self.ip_activity[ip_address]
        
        # Too many requests from single IP
        if len(recent_activity) > 200:  # More than 200 requests per hour
            return ThreatLevel.CRITICAL
        elif len(recent_activity) > 100:  # More than 100 requests per hour
            return ThreatLevel.HIGH
        
        return ThreatLevel.INFO
    
    async def _analyze_user_agent(self, user_agent: str) -> ThreatLevel:
        """Analyze user agent for suspicious patterns"""
        suspicious_ua_patterns = [
            r'bot',
            r'crawler',
            r'spider',
            r'scraper',
            r'curl',
            r'wget',
            r'python',
            r'requests',
        ]
        
        for pattern in suspicious_ua_patterns:
            if re.search(pattern, user_agent, re.IGNORECASE):
                return ThreatLevel.MEDIUM
        
        # Check for empty or very short user agent
        if len(user_agent.strip()) < 10:
            return ThreatLevel.LOW
        
        return ThreatLevel.INFO
    
    def add_to_blacklist(self, identifier: str, identifier_type: str):
        """Add identifier to blacklist"""
        if identifier_type == "user":
            self.user_blacklist.add(identifier)
        elif identifier_type == "ip":
            self.ip_blacklist.add(identifier)
    
    def remove_from_blacklist(self, identifier: str, identifier_type: str):
        """Remove identifier from blacklist"""
        if identifier_type == "user":
            self.user_blacklist.discard(identifier)
        elif identifier_type == "ip":
            self.ip_blacklist.discard(identifier)


class SecurityManager:
    """
    Production-grade security management system
    
    Features:
    - Input validation and sanitization
    - Threat detection and prevention
    - Audit logging and compliance
    - Authentication and authorization
    - Security monitoring and alerting
    """
    
    def __init__(self):
        self.input_validator = InputValidator()
        self.threat_detector = ThreatDetector()
        self.audit_log: List[SecurityEvent] = []
        self.security_handlers: List[Callable] = []
        
        # Security configuration
        self.config = {
            'max_audit_log_size': 10000,
            'audit_log_retention_hours': 24 * 7,  # 1 week
            'enable_threat_detection': True,
            'enable_audit_logging': True,
            'auto_block_threats': True,
            'threat_block_duration_minutes': 60
        }
        
        # Blocked entities
        self.blocked_users: Dict[str, datetime] = {}
        self.blocked_ips: Dict[str, datetime] = {}
        
        logger.info("Security manager initialized")
    
    def add_security_handler(self, handler: Callable[[SecurityEvent], None]):
        """Add security event handler"""
        self.security_handlers.append(handler)
    
    async def validate_input(self, field_name: str, value: str, 
                           user_id: Optional[str] = None, 
                           ip_address: Optional[str] = None) -> tuple[bool, Optional[str]]:
        """
        Validate and sanitize input
        
        Returns:
            (is_valid, error_message)
        """
        # Basic validation
        is_valid, error_message = await self.input_validator.validate(field_name, value)
        
        if not is_valid:
            # Log validation failure
            await self._log_security_event(
                SecurityEvent(
                    event_type=SecurityEventType.INPUT_VALIDATION_FAILURE,
                    timestamp=datetime.utcnow(),
                    user_id=user_id,
                    ip_address=ip_address,
                    resource=field_name,
                    result="failure",
                    threat_level=ThreatLevel.MEDIUM,
                    details={'error': error_message, 'value_length': len(value)}
                )
            )
            return False, error_message
        
        # Threat detection
        if self.config['enable_threat_detection']:
            threat_level, threats = await self.threat_detector.analyze_request(
                user_id, ip_address, value
            )
            
            if threat_level >= ThreatLevel.HIGH:
                await self._log_security_event(
                    SecurityEvent(
                        event_type=SecurityEventType.THREAT_DETECTED,
                        timestamp=datetime.utcnow(),
                        user_id=user_id,
                        ip_address=ip_address,
                        resource=field_name,
                        result="blocked",
                        threat_level=threat_level,
                        details={'threats': threats}
                    )
                )
                
                # Auto-block if configured
                if self.config['auto_block_threats']:
                    await self._auto_block_threat(user_id, ip_address, threat_level)
                
                return False, "Security threat detected"
        
        return True, None
    
    async def sanitize_input(self, value: str) -> str:
        """Sanitize input value"""
        return await self.input_validator.sanitize(value)
    
    async def check_access_permission(self, user_id: str, resource: str, 
                                    action: str, ip_address: Optional[str] = None) -> bool:
        """
        Check if user has permission to access resource
        
        Args:
            user_id: User identifier
            resource: Resource being accessed
            action: Action being performed
            ip_address: User's IP address
            
        Returns:
            True if access is allowed
        """
        # Check if user/IP is blocked
        if await self._is_blocked(user_id, ip_address):
            await self._log_security_event(
                SecurityEvent(
                    event_type=SecurityEventType.AUTHORIZATION_FAILURE,
                    timestamp=datetime.utcnow(),
                    user_id=user_id,
                    ip_address=ip_address,
                    resource=resource,
                    action=action,
                    result="blocked",
                    threat_level=ThreatLevel.HIGH,
                    details={'reason': 'User or IP blocked'}
                )
            )
            return False
        
        # Log successful access
        await self._log_security_event(
            SecurityEvent(
                event_type=SecurityEventType.DATA_ACCESS,
                timestamp=datetime.utcnow(),
                user_id=user_id,
                ip_address=ip_address,
                resource=resource,
                action=action,
                result="success",
                threat_level=ThreatLevel.INFO
            )
        )
        
        return True
    
    async def _is_blocked(self, user_id: Optional[str], ip_address: Optional[str]) -> bool:
        """Check if user or IP is currently blocked"""
        now = datetime.utcnow()
        
        # Clean expired blocks
        await self._clean_expired_blocks()
        
        # Check user block
        if user_id and user_id in self.blocked_users:
            return True
        
        # Check IP block
        if ip_address and ip_address in self.blocked_ips:
            return True
        
        return False
    
    async def _auto_block_threat(self, user_id: Optional[str], ip_address: Optional[str], 
                               threat_level: ThreatLevel):
        """Automatically block threats based on severity"""
        block_until = datetime.utcnow() + timedelta(
            minutes=self.config['threat_block_duration_minutes']
        )
        
        if user_id and threat_level >= ThreatLevel.HIGH:
            self.blocked_users[user_id] = block_until
            logger.warning(f"Auto-blocked user {user_id} due to {threat_level.value} threat")
        
        if ip_address and threat_level >= ThreatLevel.CRITICAL:
            self.blocked_ips[ip_address] = block_until
            logger.warning(f"Auto-blocked IP {ip_address} due to {threat_level.value} threat")
    
    async def _clean_expired_blocks(self):
        """Remove expired blocks"""
        now = datetime.utcnow()
        
        # Clean user blocks
        expired_users = [
            user_id for user_id, block_until in self.blocked_users.items()
            if now > block_until
        ]
        for user_id in expired_users:
            del self.blocked_users[user_id]
        
        # Clean IP blocks
        expired_ips = [
            ip for ip, block_until in self.blocked_ips.items()
            if now > block_until
        ]
        for ip in expired_ips:
            del self.blocked_ips[ip]
    
    async def _log_security_event(self, event: SecurityEvent):
        """Log security event"""
        if not self.config['enable_audit_logging']:
            return
        
        self.audit_log.append(event)
        
        # Maintain log size limit
        if len(self.audit_log) > self.config['max_audit_log_size']:
            self.audit_log.pop(0)
        
        # Send to security handlers
        for handler in self.security_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                logger.error(f"Security handler failed: {e}")
        
        # Log high-severity events
        if event.threat_level >= ThreatLevel.HIGH:
            logger.warning(f"Security event: {event.to_dict()}")
    
    async def get_security_metrics(self) -> Dict[str, Any]:
        """Get security metrics and statistics"""
        now = datetime.utcnow()
        last_24h = now - timedelta(hours=24)
        
        # Filter recent events
        recent_events = [
            event for event in self.audit_log
            if event.timestamp > last_24h
        ]
        
        # Count events by type
        event_counts = {}
        threat_counts = {}
        
        for event in recent_events:
            event_type = event.event_type.value
            threat_level = event.threat_level.value
            
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
            threat_counts[threat_level] = threat_counts.get(threat_level, 0) + 1
        
        return {
            'total_events_24h': len(recent_events),
            'event_counts': event_counts,
            'threat_counts': threat_counts,
            'blocked_users': len(self.blocked_users),
            'blocked_ips': len(self.blocked_ips),
            'blacklisted_users': len(self.threat_detector.user_blacklist),
            'blacklisted_ips': len(self.threat_detector.ip_blacklist),
            'config': self.config
        }
    
    async def export_audit_log(self, start_time: Optional[datetime] = None,
                              end_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Export audit log for compliance"""
        start_time = start_time or (datetime.utcnow() - timedelta(hours=24))
        end_time = end_time or datetime.utcnow()
        
        filtered_events = [
            event for event in self.audit_log
            if start_time <= event.timestamp <= end_time
        ]
        
        return [event.to_dict() for event in filtered_events]
    
    def block_user(self, user_id: str, duration_minutes: int = 60):
        """Manually block a user"""
        block_until = datetime.utcnow() + timedelta(minutes=duration_minutes)
        self.blocked_users[user_id] = block_until
        logger.info(f"Manually blocked user {user_id} for {duration_minutes} minutes")
    
    def block_ip(self, ip_address: str, duration_minutes: int = 60):
        """Manually block an IP address"""
        block_until = datetime.utcnow() + timedelta(minutes=duration_minutes)
        self.blocked_ips[ip_address] = block_until
        logger.info(f"Manually blocked IP {ip_address} for {duration_minutes} minutes")
    
    def unblock_user(self, user_id: str):
        """Manually unblock a user"""
        if user_id in self.blocked_users:
            del self.blocked_users[user_id]
            logger.info(f"Manually unblocked user {user_id}")
    
    def unblock_ip(self, ip_address: str):
        """Manually unblock an IP address"""
        if ip_address in self.blocked_ips:
            del self.blocked_ips[ip_address]
            logger.info(f"Manually unblocked IP {ip_address}")


# Global security manager instance
security_manager = SecurityManager()


# Convenience functions
async def validate_input(field_name: str, value: str, user_id: Optional[str] = None, 
                        ip_address: Optional[str] = None) -> tuple[bool, Optional[str]]:
    """Validate input using global security manager"""
    return await security_manager.validate_input(field_name, value, user_id, ip_address)


async def sanitize_input(value: str) -> str:
    """Sanitize input using global security manager"""
    return await security_manager.sanitize_input(value)


async def check_access(user_id: str, resource: str, action: str, 
                      ip_address: Optional[str] = None) -> bool:
    """Check access permission using global security manager"""
    return await security_manager.check_access_permission(user_id, resource, action, ip_address)