# src/comprehensive_error_handler.py
"""
Comprehensive error handling to prevent NoneType errors and improve reliability
"""

import logging
import traceback
import asyncio
from functools import wraps
from typing import Any, Callable, Optional

# Optional telegram imports for testing environments
try:
    from telegram import Update
    from telegram.ext import ContextTypes
    from telegram.constants import ParseMode
    TELEGRAM_AVAILABLE = True
except ImportError:
    # Mock classes for testing
    class Update:
        pass
    class ContextTypes:
        DEFAULT = None
        DEFAULT_TYPE = None
    class ParseMode:
        MARKDOWN_V2 = "MarkdownV2"
        MARKDOWN = "Markdown"
    TELEGRAM_AVAILABLE = False

logger = logging.getLogger(__name__)

class ErrorHandler:
    """Comprehensive error handler for the bot"""
    
    def __init__(self):
        self.error_count = 0
        self.last_errors = []
        self.max_error_history = 50
    
    def log_error(self, error: Exception, context: str = "Unknown"):
        """Log error with context"""
        self.error_count += 1
        error_info = {
            'error': str(error),
            'type': type(error).__name__,
            'context': context,
            'traceback': traceback.format_exc()
        }
        
        self.last_errors.append(error_info)
        if len(self.last_errors) > self.max_error_history:
            self.last_errors.pop(0)
        
        logger.error(f"Error in {context}: {error}")
        logger.debug(f"Full traceback: {traceback.format_exc()}")
    
    async def safe_reply(self, update: Update, message: str, parse_mode: str = ParseMode.MARKDOWN):
        """Safely reply to a message with error handling"""
        try:
            if not update or not update.effective_message:
                logger.error("Invalid update object in safe_reply")
                return False
            
            await update.effective_message.reply_text(
                message, 
                parse_mode=parse_mode
            )
            return True
            
        except Exception as e:
            logger.error(f"Error in safe_reply: {e}")
            try:
                # Fallback without parse_mode
                await update.effective_message.reply_text(message)
                return True
            except Exception as e2:
                logger.error(f"Fallback reply also failed: {e2}")
                return False
    
    async def safe_edit_message(self, message, text: str, parse_mode: str = ParseMode.MARKDOWN):
        """Safely edit a message with error handling"""
        try:
            if not message:
                logger.error("Invalid message object in safe_edit_message")
                return False
            
            await message.edit_text(text, parse_mode=parse_mode)
            return True
            
        except Exception as e:
            logger.error(f"Error in safe_edit_message: {e}")
            try:
                # Fallback without parse_mode
                await message.edit_text(text)
                return True
            except Exception as e2:
                logger.error(f"Fallback edit also failed: {e2}")
                return False
    
    async def safe_delete_message(self, message):
        """Safely delete a message with error handling"""
        try:
            if not message:
                return False
            
            await message.delete()
            return True
            
        except Exception as e:
            logger.error(f"Error deleting message: {e}")
            return False
    
    def get_error_stats(self) -> dict:
        """Get error statistics"""
        return {
            'total_errors': self.error_count,
            'recent_errors': len(self.last_errors),
            'error_types': {}
        }

# Global error handler instance
error_handler = ErrorHandler()

def safe_command(func: Callable) -> Callable:
    """Decorator for safe command execution with comprehensive error handling"""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            # Validate inputs
            if not update:
                logger.error(f"Invalid update object in {func.__name__}")
                return
            
            if not update.effective_message:
                logger.error(f"No effective_message in update for {func.__name__}")
                return
            
            if not update.effective_user:
                logger.error(f"No effective_user in update for {func.__name__}")
                return
            
            # Execute the function
            await func(update, context)
            
        except Exception as e:
            error_handler.log_error(e, f"Command: {func.__name__}")
            
            # Try to send error message
            error_message = (
                "❌ **An error occurred while processing your command.**\n\n"
                "Please try again. If the issue persists, contact support."
            )
            
            success = await error_handler.safe_reply(update, error_message)
            if not success:
                logger.error(f"Could not send error message for {func.__name__}")
    
    return wrapper

def safe_callback(func: Callable) -> Callable:
    """Decorator for safe callback query handling"""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            # Validate inputs
            if not update or not update.callback_query:
                logger.error(f"Invalid callback query in {func.__name__}")
                return
            
            # Answer the callback query first
            try:
                await update.callback_query.answer()
            except Exception as e:
                logger.warning(f"Could not answer callback query: {e}")
            
            # Execute the function
            await func(update, context)
            
        except Exception as e:
            error_handler.log_error(e, f"Callback: {func.__name__}")
            
            # Try to edit message with error
            if update.callback_query and update.callback_query.message:
                error_message = (
                    "❌ **An error occurred while processing your request.**\n\n"
                    "Please try again."
                )
                await error_handler.safe_edit_message(
                    update.callback_query.message, 
                    error_message
                )
    
    return wrapper

def safe_message_handler(func: Callable) -> Callable:
    """Decorator for safe message handling"""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            # Validate inputs
            if not update or not update.effective_message:
                logger.error(f"Invalid message in {func.__name__}")
                return
            
            # Skip if no text
            if not update.effective_message.text:
                return
            
            # Execute the function
            await func(update, context)
            
        except Exception as e:
            error_handler.log_error(e, f"Message Handler: {func.__name__}")
            
            # Try to send error message
            error_message = (
                "❌ I had trouble understanding your message. "
                "Please try rephrasing or use /help for available commands."
            )
            
            await error_handler.safe_reply(update, error_message)
    
    return wrapper

async def safe_api_call(func: Callable, *args, **kwargs) -> Any:
    """Safely execute an API call with retries"""
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
                
        except Exception as e:
            error_handler.log_error(e, f"API Call: {func.__name__} (attempt {attempt + 1})")
            
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay * (attempt + 1))
            else:
                logger.error(f"API call {func.__name__} failed after {max_retries} attempts")
                return None

def validate_update(update: Update) -> bool:
    """Validate update object"""
    if not update:
        logger.error("Update is None")
        return False
    
    if not update.effective_message:
        logger.error("Update has no effective_message")
        return False
    
    if not update.effective_user:
        logger.error("Update has no effective_user")
        return False
    
    return True

def validate_context(context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Validate context object"""
    if not context:
        logger.error("Context is None")
        return False
    
    if not context.bot:
        logger.error("Context has no bot")
        return False
    
    return True

async def safe_send_message(bot, chat_id: int, text: str, **kwargs) -> bool:
    """Safely send a message with error handling"""
    try:
        await bot.send_message(chat_id=chat_id, text=text, **kwargs)
        return True
    except Exception as e:
        error_handler.log_error(e, f"Send message to {chat_id}")
        return False

async def safe_get_chat_member(bot, chat_id: int, user_id: int):
    """Safely get chat member with error handling"""
    try:
        return await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
    except Exception as e:
        error_handler.log_error(e, f"Get chat member {user_id} in {chat_id}")
        return None

def handle_errors(default_return=None):
    """Decorator to handle errors gracefully"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {e}")
                return default_return
        return wrapper
    return decorator

async def safe_get_chat_administrators(bot, chat_id: int):
    """Safely get chat administrators with error handling"""
    try:
        return await bot.get_chat_administrators(chat_id=chat_id)
    except Exception as e:
        error_handler.log_error(e, f"Get chat administrators for {chat_id}")
        return []

def create_error_report() -> str:
    """Create a comprehensive error report"""
    stats = error_handler.get_error_stats()
    
    report = f"🔧 **Error Report**\n\n"
    report += f"Total Errors: {stats['total_errors']}\n"
    report += f"Recent Errors: {stats['recent_errors']}\n\n"
    
    if error_handler.last_errors:
        report += "**Recent Error Types:**\n"
        error_types = {}
        for error in error_handler.last_errors[-10:]:  # Last 10 errors
            error_type = error['type']
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        for error_type, count in error_types.items():
            report += f"• {error_type}: {count}\n"
    
    return report

# Utility functions for common validation patterns
def ensure_string(value: Any, default: str = "") -> str:
    """Ensure value is a string"""
    if value is None:
        return default
    return str(value)

def ensure_int(value: Any, default: int = 0) -> int:
    """Ensure value is an integer"""
    if value is None:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def ensure_float(value: Any, default: float = 0.0) -> float:
    """Ensure value is a float"""
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def ensure_list(value: Any, default: list = None) -> list:
    """Ensure value is a list"""
    if default is None:
        default = []
    
    if value is None:
        return default
    
    if isinstance(value, list):
        return value
    
    return [value]

def ensure_dict(value: Any, default: dict = None) -> dict:
    """Ensure value is a dictionary"""
    if default is None:
        default = {}
    
    if value is None:
        return default
    
    if isinstance(value, dict):
        return value
    
    return default