# src/security_auditor.py
"""
Security audit logging and monitoring for Möbius AI Assistant.
Implements comprehensive security event tracking with privacy protection.
"""
import time
import json
import hashlib
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import threading
from collections import deque
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

@dataclass
class SecurityEvent:
    """Security event data structure"""
    timestamp: float
    event_type: str
    user_id: int
    user_id_hash: str  # Hashed for privacy
    action: str
    success: bool
    ip_hash: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    risk_level: str = "low"  # low, medium, high, critical

class SecurityAuditor:
    """
    Comprehensive security audit system with privacy protection.
    Tracks sensitive operations, failed authentications, and suspicious activities.
    """
    
    def __init__(self, encryption_key: Optional[bytes] = None):
        self._lock = threading.RLock()
        self._events: deque = deque(maxlen=10000)  # Limit memory usage
        self._failed_attempts: Dict[int, List[float]] = {}  # user_id -> timestamps
        self._suspicious_ips: Dict[str, int] = {}  # ip_hash -> count
        
        # Initialize encryption for sensitive audit data
        self._fernet = None
        if encryption_key:
            try:
                self._fernet = Fernet(encryption_key)
            except Exception as e:
                logger.error(f"Failed to initialize audit encryption: {e}")
        
        # Security thresholds
        self._max_failed_attempts = 5
        self._failed_attempt_window = 300  # 5 minutes
        self._suspicious_ip_threshold = 10
        
        logger.info("Security auditor initialized")
    
    def log_authentication_attempt(self, user_id: int, action: str, success: bool, 
                                 ip_address: Optional[str] = None, details: Optional[Dict] = None):
        """Log authentication attempts with rate limiting detection"""
        ip_hash = self._hash_ip(ip_address) if ip_address else None
        
        # Track failed attempts for rate limiting
        if not success:
            self._track_failed_attempt(user_id, ip_hash)
        
        event = SecurityEvent(
            timestamp=time.time(),
            event_type="authentication",
            user_id=user_id,
            user_id_hash=self._hash_user_id(user_id),
            action=action,
            success=success,
            ip_hash=ip_hash,
            details=self._sanitize_details(details),
            risk_level=self._assess_auth_risk(user_id, success, ip_hash)
        )
        
        self._store_event(event)
        
        # Alert on suspicious activity
        if event.risk_level in ["high", "critical"]:
            self._alert_suspicious_activity(event)
    
    def log_sensitive_action(self, user_id: int, action: str, success: bool,
                           details: Optional[Dict] = None, ip_address: Optional[str] = None):
        """Log sensitive operations like wallet creation, API key changes"""
        ip_hash = self._hash_ip(ip_address) if ip_address else None
        
        event = SecurityEvent(
            timestamp=time.time(),
            event_type="sensitive_operation",
            user_id=user_id,
            user_id_hash=self._hash_user_id(user_id),
            action=action,
            success=success,
            ip_hash=ip_hash,
            details=self._sanitize_details(details),
            risk_level=self._assess_sensitive_risk(action, success)
        )
        
        self._store_event(event)
        
        if not success or event.risk_level == "critical":
            self._alert_suspicious_activity(event)
    
    def log_admin_action(self, user_id: int, action: str, success: bool,
                        target_data: Optional[str] = None, ip_address: Optional[str] = None):
        """Log administrative actions with enhanced monitoring"""
        ip_hash = self._hash_ip(ip_address) if ip_address else None
        
        event = SecurityEvent(
            timestamp=time.time(),
            event_type="admin_action",
            user_id=user_id,
            user_id_hash=self._hash_user_id(user_id),
            action=action,
            success=success,
            ip_hash=ip_hash,
            details={"target": target_data} if target_data else None,
            risk_level="high" if not success else "medium"
        )
        
        self._store_event(event)
        
        # All admin actions are logged as high priority
        logger.warning(f"Admin action: {action} by user {self._hash_user_id(user_id)} - Success: {success}")
    
    def log_data_access(self, user_id: int, data_type: str, action: str, success: bool):
        """Log data access events for compliance"""
        event = SecurityEvent(
            timestamp=time.time(),
            event_type="data_access",
            user_id=user_id,
            user_id_hash=self._hash_user_id(user_id),
            action=f"{action}_{data_type}",
            success=success,
            details={"data_type": data_type},
            risk_level="low"
        )
        
        self._store_event(event)
    
    def check_user_security_status(self, user_id: int) -> Dict[str, Any]:
        """Check security status for a specific user"""
        with self._lock:
            user_events = [e for e in self._events if e.user_id == user_id]
            recent_events = [e for e in user_events if time.time() - e.timestamp < 3600]  # Last hour
            
            failed_auths = len([e for e in recent_events if e.event_type == "authentication" and not e.success])
            sensitive_ops = len([e for e in recent_events if e.event_type == "sensitive_operation"])
            
            risk_score = self._calculate_user_risk_score(user_id)
            
            return {
                "user_id_hash": self._hash_user_id(user_id),
                "recent_failed_auths": failed_auths,
                "recent_sensitive_ops": sensitive_ops,
                "risk_score": risk_score,
                "is_suspicious": risk_score > 70,
                "last_activity": max([e.timestamp for e in user_events]) if user_events else None
            }
    
    def get_security_summary(self) -> Dict[str, Any]:
        """Get overall security summary for admin dashboard"""
        with self._lock:
            now = time.time()
            recent_events = [e for e in self._events if now - e.timestamp < 3600]  # Last hour
            
            # Count events by type and risk level
            event_counts = {}
            risk_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
            
            for event in recent_events:
                event_counts[event.event_type] = event_counts.get(event.event_type, 0) + 1
                risk_counts[event.risk_level] += 1
            
            # Identify top suspicious IPs (anonymized)
            suspicious_ips = sorted(self._suspicious_ips.items(), key=lambda x: x[1], reverse=True)[:5]
            
            return {
                "summary": {
                    "total_events_last_hour": len(recent_events),
                    "high_risk_events": risk_counts["high"] + risk_counts["critical"],
                    "failed_authentications": len([e for e in recent_events if e.event_type == "authentication" and not e.success]),
                    "suspicious_ips_count": len([ip for ip, count in self._suspicious_ips.items() if count >= self._suspicious_ip_threshold])
                },
                "event_breakdown": event_counts,
                "risk_breakdown": risk_counts,
                "top_suspicious_ips": [{"ip_hash": ip_hash[:16] + "...", "count": count} for ip_hash, count in suspicious_ips]
            }
    
    def export_audit_log(self, start_time: Optional[float] = None, end_time: Optional[float] = None) -> List[Dict]:
        """Export audit log for compliance (anonymized)"""
        with self._lock:
            events = list(self._events)
            
            if start_time:
                events = [e for e in events if e.timestamp >= start_time]
            if end_time:
                events = [e for e in events if e.timestamp <= end_time]
            
            # Return anonymized data
            return [
                {
                    "timestamp": datetime.fromtimestamp(e.timestamp, tz=timezone.utc).isoformat(),
                    "event_type": e.event_type,
                    "user_id_hash": e.user_id_hash,
                    "action": e.action,
                    "success": e.success,
                    "risk_level": e.risk_level,
                    "ip_hash": e.ip_hash[:16] + "..." if e.ip_hash else None
                }
                for e in events
            ]
    
    def _store_event(self, event: SecurityEvent):
        """Store security event with optional encryption"""
        with self._lock:
            self._events.append(event)
            
            # Log high-risk events immediately
            if event.risk_level in ["high", "critical"]:
                logger.warning(f"High-risk security event: {event.event_type} - {event.action} by {event.user_id_hash}")
    
    def _track_failed_attempt(self, user_id: int, ip_hash: Optional[str]):
        """Track failed authentication attempts"""
        now = time.time()
        
        # Clean old attempts
        if user_id in self._failed_attempts:
            self._failed_attempts[user_id] = [
                t for t in self._failed_attempts[user_id] 
                if now - t < self._failed_attempt_window
            ]
        else:
            self._failed_attempts[user_id] = []
        
        # Add new attempt
        self._failed_attempts[user_id].append(now)
        
        # Track suspicious IPs
        if ip_hash:
            self._suspicious_ips[ip_hash] = self._suspicious_ips.get(ip_hash, 0) + 1
    
    def _assess_auth_risk(self, user_id: int, success: bool, ip_hash: Optional[str]) -> str:
        """Assess risk level for authentication events"""
        if success:
            return "low"
        
        # Check for repeated failures
        failed_count = len(self._failed_attempts.get(user_id, []))
        if failed_count >= self._max_failed_attempts:
            return "critical"
        elif failed_count >= 3:
            return "high"
        
        # Check for suspicious IP
        if ip_hash and self._suspicious_ips.get(ip_hash, 0) >= self._suspicious_ip_threshold:
            return "high"
        
        return "medium"
    
    def _assess_sensitive_risk(self, action: str, success: bool) -> str:
        """Assess risk level for sensitive operations"""
        high_risk_actions = ["create_wallet", "set_api_key", "admin_command"]
        
        if not success:
            return "high"
        
        if any(risk_action in action.lower() for risk_action in high_risk_actions):
            return "medium"
        
        return "low"
    
    def _calculate_user_risk_score(self, user_id: int) -> int:
        """Calculate risk score for a user (0-100)"""
        with self._lock:
            user_events = [e for e in self._events if e.user_id == user_id]
            recent_events = [e for e in user_events if time.time() - e.timestamp < 3600]
            
            score = 0
            
            # Failed authentications
            failed_auths = len([e for e in recent_events if e.event_type == "authentication" and not e.success])
            score += min(failed_auths * 20, 60)
            
            # High-risk events
            high_risk_events = len([e for e in recent_events if e.risk_level in ["high", "critical"]])
            score += min(high_risk_events * 15, 40)
            
            # Rapid successive actions (potential automation)
            if len(recent_events) > 20:
                score += 20
            
            return min(score, 100)
    
    def _alert_suspicious_activity(self, event: SecurityEvent):
        """Alert on suspicious security events"""
        alert_msg = (
            f"SECURITY ALERT: {event.event_type} - {event.action}\n"
            f"User: {event.user_id_hash}\n"
            f"Risk Level: {event.risk_level}\n"
            f"Success: {event.success}\n"
            f"Time: {datetime.fromtimestamp(event.timestamp, tz=timezone.utc).isoformat()}"
        )
        
        logger.critical(alert_msg)
        
        # In production, this could send alerts to admin channels
        # or external monitoring systems
    
    def _hash_user_id(self, user_id: int) -> str:
        """Hash user ID for privacy protection"""
        return hashlib.sha256(f"user_{user_id}_salt".encode()).hexdigest()[:16]
    
    def _hash_ip(self, ip_address: str) -> str:
        """Hash IP address for privacy protection"""
        return hashlib.sha256(f"ip_{ip_address}_salt".encode()).hexdigest()[:16]
    
    def _sanitize_details(self, details: Optional[Dict]) -> Optional[Dict]:
        """Sanitize sensitive details for logging"""
        if not details:
            return None
        
        # Remove sensitive keys
        sensitive_keys = ["password", "private_key", "api_key", "token", "secret"]
        sanitized = {}
        
        for key, value in details.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = "[REDACTED]"
            elif isinstance(value, str) and len(value) > 100:
                sanitized[key] = value[:100] + "..."
            else:
                sanitized[key] = value
        
        return sanitized

# Global security auditor instance
security_auditor = SecurityAuditor()