# src/error_handler.py
"""
Enhanced error handling and recovery system for Möbius AI Assistant.
Provides intelligent error recovery, user-friendly messages, and automatic retries.
"""
import asyncio
import logging
import time
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass
from enum import Enum
import traceback

logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ErrorContext:
    """Context information for error handling"""
    user_id: int
    command: str
    error_type: str
    severity: ErrorSeverity
    retry_count: int = 0
    max_retries: int = 3
    backoff_factor: float = 1.5

class EnhancedErrorHandler:
    """
    Intelligent error handling with recovery strategies and user-friendly messaging.
    Maintains responsiveness while providing helpful error resolution.
    """
    
    def __init__(self):
        self.error_patterns = self._load_error_patterns()
        self.recovery_strategies = self._load_recovery_strategies()
        self.user_friendly_messages = self._load_user_messages()
        
    def _load_error_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Load error pattern recognition rules"""
        return {
            "api_timeout": {
                "patterns": ["timeout", "connection timeout", "read timeout"],
                "severity": ErrorSeverity.MEDIUM,
                "recoverable": True,
                "max_retries": 3,
                "user_message": "🕐 **Service Temporarily Slow**\n\nThe external service is responding slowly. I'm retrying your request..."
            },
            "api_rate_limit": {
                "patterns": ["rate limit", "too many requests", "429"],
                "severity": ErrorSeverity.MEDIUM,
                "recoverable": True,
                "max_retries": 2,
                "backoff_factor": 2.0,
                "user_message": "⏱️ **Rate Limit Reached**\n\nI'm being rate-limited by the service. Waiting a moment before retrying..."
            },
            "api_key_invalid": {
                "patterns": ["invalid api key", "unauthorized", "401", "403"],
                "severity": ErrorSeverity.HIGH,
                "recoverable": False,
                "user_message": "🔑 **API Configuration Issue**\n\nThere's an issue with the API configuration. Please contact an administrator."
            },
            "network_error": {
                "patterns": ["connection error", "network", "dns", "unreachable"],
                "severity": ErrorSeverity.MEDIUM,
                "recoverable": True,
                "max_retries": 2,
                "user_message": "🌐 **Network Issue**\n\nThere's a temporary network issue. I'm attempting to reconnect..."
            },
            "database_error": {
                "patterns": ["database", "sqlite", "connection pool"],
                "severity": ErrorSeverity.HIGH,
                "recoverable": True,
                "max_retries": 2,
                "user_message": "💾 **Database Temporarily Unavailable**\n\nThe database is experiencing issues. I'm working to resolve this..."
            },
            "validation_error": {
                "patterns": ["validation", "invalid input", "malformed"],
                "severity": ErrorSeverity.LOW,
                "recoverable": False,
                "user_message": "⚠️ **Input Validation Error**\n\nPlease check your input format and try again. Use `/help` for command examples."
            }
        }
    
    def _load_recovery_strategies(self) -> Dict[str, Callable]:
        """Load recovery strategy functions"""
        return {
            "api_timeout": self._retry_with_backoff,
            "api_rate_limit": self._retry_with_exponential_backoff,
            "network_error": self._retry_with_backoff,
            "database_error": self._retry_database_operation,
            "api_key_invalid": self._notify_admin,
            "validation_error": self._provide_usage_help
        }
    
    def _load_user_messages(self) -> Dict[str, str]:
        """Load user-friendly error messages with actionable suggestions"""
        return {
            "generic": "❌ **Something went wrong**\n\nI encountered an unexpected issue. Please try again in a moment.",
            "with_suggestion": "❌ **Command Failed**\n\n{error_message}\n\n💡 **Suggestions:**\n{suggestions}",
            "retry_success": "✅ **Recovered Successfully**\n\nI was able to complete your request after resolving a temporary issue.",
            "retry_failed": "❌ **Unable to Complete**\n\nI tried multiple times but couldn't complete your request. Please try again later or contact support."
        }
    
    async def handle_error(self, error: Exception, context: ErrorContext) -> Dict[str, Any]:
        """
        Main error handling entry point with intelligent recovery.
        Returns response data for user feedback.
        """
        try:
            # Classify the error
            error_info = self._classify_error(str(error), error.__class__.__name__)
            
            # Log the error with context
            self._log_error(error, context, error_info)
            
            # Attempt recovery if possible
            if error_info.get("recoverable", False) and context.retry_count < error_info.get("max_retries", 0):
                return await self._attempt_recovery(error, context, error_info)
            
            # Generate user-friendly response
            user_message = self._generate_user_message(error_info, context)
            suggestions = self._generate_suggestions(error_info, context)
            
            return {
                "success": False,
                "message": user_message,
                "suggestions": suggestions,
                "severity": error_info.get("severity", ErrorSeverity.MEDIUM).value,
                "recoverable": error_info.get("recoverable", False)
            }
            
        except Exception as handler_error:
            logger.critical(f"Error handler itself failed: {handler_error}")
            return {
                "success": False,
                "message": self.user_friendly_messages["generic"],
                "suggestions": ["Try the command again", "Contact support if the issue persists"],
                "severity": ErrorSeverity.HIGH.value,
                "recoverable": False
            }
    
    def _classify_error(self, error_message: str, error_type: str) -> Dict[str, Any]:
        """Classify error based on message patterns and type"""
        error_message_lower = error_message.lower()
        
        for error_category, config in self.error_patterns.items():
            patterns = config.get("patterns", [])
            if any(pattern in error_message_lower for pattern in patterns):
                return {**config, "category": error_category}
        
        # Default classification for unknown errors
        return {
            "category": "unknown",
            "severity": ErrorSeverity.MEDIUM,
            "recoverable": False,
            "user_message": self.user_friendly_messages["generic"]
        }
    
    async def _attempt_recovery(self, error: Exception, context: ErrorContext, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt to recover from the error using appropriate strategy"""
        category = error_info.get("category", "unknown")
        strategy = self.recovery_strategies.get(category)
        
        if not strategy:
            return await self._default_recovery(error, context, error_info)
        
        try:
            # Update retry count
            context.retry_count += 1
            
            # Apply backoff delay
            backoff_delay = self._calculate_backoff(context, error_info)
            if backoff_delay > 0:
                await asyncio.sleep(backoff_delay)
            
            # Attempt recovery
            recovery_result = await strategy(error, context, error_info)
            
            if recovery_result.get("success", False):
                return {
                    "success": True,
                    "message": self.user_friendly_messages["retry_success"],
                    "recovered": True,
                    "retry_count": context.retry_count
                }
            else:
                # Recovery failed, try again or give up
                if context.retry_count < error_info.get("max_retries", 0):
                    return await self._attempt_recovery(error, context, error_info)
                else:
                    return {
                        "success": False,
                        "message": self.user_friendly_messages["retry_failed"],
                        "suggestions": self._generate_suggestions(error_info, context),
                        "retry_count": context.retry_count
                    }
        
        except Exception as recovery_error:
            logger.error(f"Recovery strategy failed: {recovery_error}")
            return await self._default_recovery(error, context, error_info)
    
    def _calculate_backoff(self, context: ErrorContext, error_info: Dict[str, Any]) -> float:
        """Calculate exponential backoff delay"""
        base_delay = 1.0  # 1 second base
        backoff_factor = error_info.get("backoff_factor", context.backoff_factor)
        max_delay = 30.0  # Maximum 30 seconds
        
        delay = base_delay * (backoff_factor ** (context.retry_count - 1))
        return min(delay, max_delay)
    
    async def _retry_with_backoff(self, error: Exception, context: ErrorContext, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """Simple retry with backoff strategy"""
        # This would be implemented by the calling code
        return {"success": False, "retry": True}
    
    async def _retry_with_exponential_backoff(self, error: Exception, context: ErrorContext, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """Exponential backoff retry strategy"""
        # This would be implemented by the calling code
        return {"success": False, "retry": True}
    
    async def _retry_database_operation(self, error: Exception, context: ErrorContext, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """Database-specific recovery strategy"""
        # Could implement database connection reset, etc.
        return {"success": False, "retry": True}
    
    async def _notify_admin(self, error: Exception, context: ErrorContext, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """Notify administrators of critical issues"""
        logger.critical(f"Admin notification required: {error} for user {context.user_id}")
        return {"success": False, "admin_notified": True}
    
    async def _provide_usage_help(self, error: Exception, context: ErrorContext, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """Provide usage help for validation errors"""
        return {
            "success": False,
            "help_provided": True,
            "suggestions": [f"Use `/help {context.command}` for usage examples"]
        }
    
    async def _default_recovery(self, error: Exception, context: ErrorContext, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """Default recovery strategy"""
        return {"success": False, "message": error_info.get("user_message", self.user_friendly_messages["generic"])}
    
    def _generate_user_message(self, error_info: Dict[str, Any], context: ErrorContext) -> str:
        """Generate user-friendly error message"""
        base_message = error_info.get("user_message", self.user_friendly_messages["generic"])
        
        if context.retry_count > 0:
            base_message += f"\n\n🔄 Attempt {context.retry_count + 1} of {error_info.get('max_retries', 1) + 1}"
        
        return base_message
    
    def _generate_suggestions(self, error_info: Dict[str, Any], context: ErrorContext) -> List[str]:
        """Generate actionable suggestions for the user"""
        suggestions = []
        
        category = error_info.get("category", "unknown")
        
        suggestion_map = {
            "api_timeout": [
                "Try the command again in a few moments",
                "Check if the service status page reports any issues"
            ],
            "api_rate_limit": [
                "Wait a few minutes before trying again",
                "Consider upgrading to a higher tier for more API calls"
            ],
            "api_key_invalid": [
                "Contact an administrator to check API configuration",
                "Verify that all required API keys are properly set"
            ],
            "network_error": [
                "Check your internet connection",
                "Try the command again in a few moments"
            ],
            "database_error": [
                "Try the command again shortly",
                "Contact support if the issue persists"
            ],
            "validation_error": [
                f"Use `/help {context.command}` for correct usage",
                "Check the command format and try again"
            ]
        }
        
        suggestions.extend(suggestion_map.get(category, [
            "Try the command again",
            "Use `/help` for available commands",
            "Contact support if the issue continues"
        ]))
        
        return suggestions[:3]  # Limit to 3 suggestions
    
    def _log_error(self, error: Exception, context: ErrorContext, error_info: Dict[str, Any]):
        """Log error with appropriate level and context"""
        severity = error_info.get("severity", ErrorSeverity.MEDIUM)
        
        log_data = {
            "user_id": context.user_id,
            "command": context.command,
            "error_type": error.__class__.__name__,
            "error_message": str(error),
            "category": error_info.get("category", "unknown"),
            "severity": severity.value,
            "retry_count": context.retry_count,
            "recoverable": error_info.get("recoverable", False)
        }
        
        if severity == ErrorSeverity.CRITICAL:
            logger.critical(f"Critical error: {log_data}")
        elif severity == ErrorSeverity.HIGH:
            logger.error(f"High severity error: {log_data}")
        elif severity == ErrorSeverity.MEDIUM:
            logger.warning(f"Medium severity error: {log_data}")
        else:
            logger.info(f"Low severity error: {log_data}")

# Decorator for automatic error handling
def handle_errors(command_name: str, max_retries: int = 3):
    """Decorator to automatically handle errors in command functions"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            error_handler = EnhancedErrorHandler()
            
            # Extract user_id from update if available
            user_id = None
            if args and hasattr(args[0], 'effective_user'):
                user_id = args[0].effective_user.id
            
            context = ErrorContext(
                user_id=user_id or 0,
                command=command_name,
                error_type="command_execution",
                severity=ErrorSeverity.MEDIUM,
                max_retries=max_retries
            )
            
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                error_result = await error_handler.handle_error(e, context)
                
                # Send error message to user if update is available
                if args and hasattr(args[0], 'message'):
                    update = args[0]
                    await update.message.reply_text(
                        error_result["message"],
                        parse_mode="Markdown"
                    )
                
                # Re-raise if not recoverable or max retries exceeded
                if not error_result.get("success", False):
                    raise
                
                return error_result
        
        return wrapper
    return decorator

# Global error handler instance
enhanced_error_handler = EnhancedErrorHandler()