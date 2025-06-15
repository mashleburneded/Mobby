# src/group_chat_manager.py
"""
Enhanced Group Chat Management for Möbius AI Assistant
Handles intelligent group chat behavior, mention detection, silent learning, and context awareness
"""

import logging
import re
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from telegram import Update, User, Chat
from telegram.ext import ContextTypes
from conversation_intelligence import stream_conversation_message

logger = logging.getLogger(__name__)

class EnhancedGroupChatManager:
    """
    Enhanced group chat manager that:
    1. Properly detects when to respond vs. silently observe
    2. Streams all conversations for learning
    3. Maintains context awareness
    4. Prevents inappropriate responses
    """
    
    def __init__(self, bot_username: str = "mobius_ai_bot"):
        self.bot_username = bot_username.lower()
        
        # Mention patterns - more comprehensive
        self.mention_patterns = [
            rf"@{self.bot_username}",
            r"@mobius\b",
            r"@mobius_ai_bot\b",
            r"@möbius\b",
            r"hey\s+mobius\b",
            r"hey\s+bot\b",
            r"hey\s+ai\b",
            r"ai\s+assistant\b",
            r"crypto\s+bot\b",
            r"bot\s+help\b",
            r"ai\s+help\b"
        ]
        
        # Compile patterns for efficiency
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.mention_patterns]
        
        # Track group conversations and contexts
        self.group_contexts: Dict[int, Dict[str, Any]] = {}
        self.silent_learning_enabled = True
        self.response_cooldown: Dict[int, datetime] = {}
        
        # Behavior configuration
        self.config = {
            "silent_learning": True,
            "respond_to_mentions": True,
            "respond_to_replies": True,
            "respond_to_commands": True,
            "respond_to_urgent_crypto": False,  # Disabled to prevent spam
            "contextual_responses": False,  # Disabled to prevent spam
            "cooldown_seconds": 30,  # Minimum time between responses
            "max_responses_per_hour": 10,  # Rate limiting
        }
    
    async def process_group_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Tuple[bool, str]:
        """
        Process a group message and determine response strategy
        Returns: (should_respond, reason)
        """
        
        if not update.effective_message or not update.effective_chat:
            return False, "No message or chat"
        
        message = update.effective_message
        chat = update.effective_chat
        user = update.effective_user
        
        # Always respond in private chats
        if chat.type == 'private':
            return True, "Private chat"
        
        # Stream message for learning (ALWAYS do this)
        await self._stream_message_for_learning(message, chat, user)
        
        # For group chats, apply strict response rules
        text = message.text or message.caption or ""
        
        # Check cooldown first
        if not self._check_response_cooldown(chat.id):
            return False, "Response cooldown active"
        
        # 1. Commands - ALWAYS respond
        if text.startswith('/'):
            self._update_response_cooldown(chat.id)
            return True, "Command"
        
        # 2. Direct mention of bot - ALWAYS respond
        if self._is_bot_mentioned(text):
            self._update_response_cooldown(chat.id)
            return True, "Bot mentioned"
        
        # 3. Reply to bot's message - ALWAYS respond
        if message.reply_to_message and message.reply_to_message.from_user:
            if (message.reply_to_message.from_user.username and 
                message.reply_to_message.from_user.username.lower() == self.bot_username):
                self._update_response_cooldown(chat.id)
                return True, "Reply to bot"
        
        # 4. All other cases - SILENT LEARNING ONLY
        return False, "Silent learning mode"
    
    async def _stream_message_for_learning(self, message, chat, user):
        """Stream message to conversation intelligence for learning"""
        try:
            if self.silent_learning_enabled:
                await stream_conversation_message(
                    message_id=str(message.message_id),
                    user_id=user.id,
                    username=user.username or user.first_name or f"user_{user.id}",
                    chat_id=chat.id,
                    chat_type=chat.type,
                    text=message.text or message.caption or "",
                    is_bot_message=user.is_bot,
                    reply_to_message_id=str(message.reply_to_message.message_id) if message.reply_to_message else None
                )
        except Exception as e:
            logger.error(f"Error streaming message for learning: {e}")
    
    def _is_bot_mentioned(self, text: str) -> bool:
        """Check if bot is mentioned in text"""
        if not text:
            return False
        
        text_lower = text.lower()
        
        # Check compiled patterns
        for pattern in self.compiled_patterns:
            if pattern.search(text_lower):
                return True
        
        return False
    
    def _check_response_cooldown(self, chat_id: int) -> bool:
        """Check if bot can respond (not in cooldown)"""
        if chat_id not in self.response_cooldown:
            return True
        
        last_response = self.response_cooldown[chat_id]
        cooldown_period = timedelta(seconds=self.config["cooldown_seconds"])
        
        return datetime.now() - last_response > cooldown_period
    
    def _update_response_cooldown(self, chat_id: int):
        """Update the response cooldown for a chat"""
        self.response_cooldown[chat_id] = datetime.now()
    
    def update_group_context(self, chat_id: int, message, bot_responded: bool = False):
        """Update group context with message information"""
        try:
            if chat_id not in self.group_contexts:
                self.group_contexts[chat_id] = {
                    "last_activity": datetime.now(),
                    "message_count": 0,
                    "bot_responses": 0,
                    "participants": set(),
                    "topics": [],
                    "last_bot_response": None
                }
            
            context = self.group_contexts[chat_id]
            context["last_activity"] = datetime.now()
            context["message_count"] += 1
            
            if message.from_user:
                context["participants"].add(message.from_user.id)
            
            if bot_responded:
                context["bot_responses"] += 1
                context["last_bot_response"] = datetime.now()
            
        except Exception as e:
            logger.error(f"Error updating group context: {e}")
    
    def format_group_response(self, response: str, username: str, strategy: str = "default") -> str:
        """Format response for group chat"""
        try:
            # Don't add unnecessary prefixes for group responses
            # Keep responses clean and natural
            return response
            
        except Exception as e:
            logger.error(f"Error formatting group response: {e}")
            return response
    
    def get_group_response_strategy(self, chat_id: int, message) -> str:
        """Get response strategy for group chat"""
        try:
            context = self.group_contexts.get(chat_id, {})
            
            # Simple strategy - just respond naturally
            return "natural"
            
        except Exception as e:
            logger.error(f"Error getting group response strategy: {e}")
            return "default"
    
    def _should_respond_to_message(self, text: str, chat_type: str, is_mentioned: bool = False, is_reply: bool = False) -> bool:
        """Determine if bot should respond to a message"""
        # Always respond in private chats
        if chat_type == "private":
            return True
        
        # In groups, only respond to:
        # 1. Direct mentions
        # 2. Replies to bot messages
        # 3. Commands
        if chat_type in ["group", "supergroup"]:
            # Check for mentions
            if is_mentioned or self._is_bot_mentioned(text):
                return True
            
            # Check for replies to bot
            if is_reply:
                return True
            
            # Check for commands
            if text and text.startswith("/"):
                return True
            
            # Otherwise, silent learning mode
            return False
        
        # Default to not responding
        return False

# Create global instance
enhanced_group_manager = EnhancedGroupChatManager()

# Export functions for backward compatibility
def should_respond_in_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Tuple[bool, str]:
    """Determine if bot should respond in group chat"""
    import asyncio
    
    # Create event loop if none exists
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    # Run the async function
    return loop.run_until_complete(
        enhanced_group_manager.process_group_message(update, context)
    )

def update_group_context(chat_id: int, message, bot_responded: bool = False):
    """Update group context"""
    enhanced_group_manager.update_group_context(chat_id, message, bot_responded)

def format_group_response(response: str, username: str, strategy: str = "default") -> str:
    """Format response for group chat"""
    return enhanced_group_manager.format_group_response(response, username, strategy)

def get_group_response_strategy(chat_id: int, message) -> str:
    """Get response strategy for group chat"""
    return enhanced_group_manager.get_group_response_strategy(chat_id, message)

def should_respond_to_message(text: str, chat_type: str, is_mentioned: bool = False, is_reply: bool = False) -> bool:
    """Determine if bot should respond to a message"""
    return enhanced_group_manager._should_respond_to_message(text, chat_type, is_mentioned, is_reply)