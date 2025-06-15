# src/contextual_ai.py
"""
Contextual AI system for Möbius AI Assistant.
Implements conversation memory, context-aware responses, and predictive analytics.
"""
import asyncio
import logging
import time
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from collections import deque, defaultdict
import hashlib
from datetime import datetime, timedelta

from ai_providers import get_ai_response
from enhanced_db import enhanced_db

logger = logging.getLogger(__name__)

@dataclass
class ConversationContext:
    """Conversation context data structure"""
    user_id: int
    messages: deque  # Recent messages
    topics: List[str]  # Identified topics
    intent_history: List[str]  # Previous intents
    preferences: Dict[str, Any]  # User preferences
    last_activity: float
    session_start: float
    command_frequency: Dict[str, int]  # Command usage patterns

@dataclass
class UserIntent:
    """User intent classification"""
    intent_type: str
    confidence: float
    entities: Dict[str, Any]
    suggested_actions: List[str]

class ContextualAI:
    """
    Advanced AI system with conversation memory and context awareness.
    Provides personalized responses based on user history and behavior patterns.
    """
    
    def __init__(self):
        self.conversation_contexts: Dict[int, ConversationContext] = {}
        self.intent_patterns = self._load_intent_patterns()
        self.topic_keywords = self._load_topic_keywords()
        
        # Context management settings
        self.max_context_messages = 50
        self.context_timeout = 3600  # 1 hour
        self.memory_cleanup_interval = 300  # 5 minutes
        
        # Start cleanup task (only if event loop is running)
        self._cleanup_task = None
        try:
            loop = asyncio.get_running_loop()
            self._cleanup_task = loop.create_task(self._periodic_cleanup())
        except RuntimeError:
            # No event loop running, cleanup will be started later
            logger.debug("No event loop running, cleanup task will be started later")
        
        logger.info("Contextual AI system initialized")
    
    def start_cleanup_task(self):
        """Start the cleanup task if not already running"""
        if self._cleanup_task is None or self._cleanup_task.done():
            try:
                loop = asyncio.get_running_loop()
                self._cleanup_task = loop.create_task(self._periodic_cleanup())
            except RuntimeError:
                logger.debug("No event loop available to start cleanup task")
    
    async def process_message(self, user_id: int, message: str, command: Optional[str] = None) -> Dict[str, Any]:
        """
        Process user message with context awareness.
        Returns enhanced response with suggestions and context.
        """
        # Get or create conversation context
        context = self._get_or_create_context(user_id)
        
        # Update context with new message
        self._update_context(context, message, command)
        
        # Analyze user intent
        intent = await self._analyze_intent(message, context)
        
        # Generate contextual response
        response_data = await self._generate_contextual_response(message, context, intent)
        
        # Update user preferences based on interaction
        self._update_user_preferences(context, intent, command)
        
        return {
            "response": response_data["response"],
            "suggestions": response_data["suggestions"],
            "intent": asdict(intent),
            "context_summary": self._get_context_summary(context)
        }
    
    async def predict_user_needs(self, user_id: int) -> List[str]:
        """Predict what the user might want to do next based on patterns"""
        context = self.conversation_contexts.get(user_id)
        if not context:
            return []
        
        predictions = []
        
        # Analyze recent command patterns
        recent_commands = list(context.command_frequency.keys())
        
        # Pattern-based predictions
        if "llama" in recent_commands and "arkham" not in recent_commands:
            predictions.append("🔍 Try `/arkham` to research the protocol's main wallet")
        
        if "arkham" in recent_commands and "alert" not in recent_commands:
            predictions.append("⚠️ Set up alerts with `/alert` for the wallets you researched")
        
        if "create_wallet" in recent_commands:
            predictions.append("💰 Check your wallet balance or set up monitoring")
        
        # Time-based predictions
        current_hour = datetime.now().hour
        if 9 <= current_hour <= 17:  # Business hours
            if "schedule" not in recent_commands:
                predictions.append("📅 Share your calendar with `/set_calendly`")
        
        # Topic-based predictions
        if "defi" in context.topics and "tvl" not in recent_commands:
            predictions.append("📊 Check TVL data for DeFi protocols")
        
        return predictions[:3]  # Limit to top 3 predictions
    
    async def get_personalized_help(self, user_id: int) -> str:
        """Generate personalized help based on user's usage patterns"""
        context = self.conversation_contexts.get(user_id)
        
        if not context:
            return self._get_default_help()
        
        # Analyze user's command usage
        used_commands = set(context.command_frequency.keys())
        all_commands = {
            "llama", "arkham", "nansen", "alert", "create_wallet", 
            "set_calendly", "schedule", "summarynow", "premium"
        }
        unused_commands = all_commands - used_commands
        
        help_text = "🎯 **Personalized Help**\n\n"
        
        # Show most used commands
        if context.command_frequency:
            top_commands = sorted(
                context.command_frequency.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:3]
            
            help_text += "🔥 **Your Most Used Commands:**\n"
            for cmd, count in top_commands:
                help_text += f"• `/{cmd}` (used {count} times)\n"
            help_text += "\n"
        
        # Suggest unused features
        if unused_commands:
            help_text += "💡 **Features You Haven't Tried:**\n"
            feature_descriptions = {
                "llama": "📊 Get DeFi protocol data (TVL, revenue, raises)",
                "arkham": "🔍 Research wallet addresses and entities",
                "nansen": "🏷️ Get wallet labels and analytics",
                "alert": "⚠️ Set up transaction alerts for wallets",
                "create_wallet": "💰 Generate secure Ethereum wallets",
                "set_calendly": "📅 Share your scheduling link",
                "schedule": "🤝 Find others' calendar links",
                "summarynow": "📋 Get conversation summaries",
                "premium": "⭐ Check your subscription status"
            }
            
            for cmd in list(unused_commands)[:3]:
                if cmd in feature_descriptions:
                    help_text += f"• `/{cmd}` - {feature_descriptions[cmd]}\n"
            help_text += "\n"
        
        # Add contextual tips based on topics
        if "crypto" in context.topics or "defi" in context.topics:
            help_text += "💡 **Crypto Research Tips:**\n"
            help_text += "• Use `/llama tvl protocol_name` for TVL data\n"
            help_text += "• Research wallets with `/arkham wallet_address`\n"
            help_text += "• Set alerts with `/alert address amount`\n"
        
        return help_text
    
    def get_user_analytics(self, user_id: int) -> Dict[str, Any]:
        """Get analytics for a specific user"""
        context = self.conversation_contexts.get(user_id)
        
        if not context:
            return {"error": "No conversation data available"}
        
        session_duration = time.time() - context.session_start
        
        return {
            "session_duration_minutes": session_duration / 60,
            "messages_in_session": len(context.messages),
            "topics_discussed": context.topics,
            "command_usage": dict(context.command_frequency),
            "most_used_command": max(context.command_frequency.items(), key=lambda x: x[1])[0] if context.command_frequency else None,
            "preferences": context.preferences,
            "last_activity": datetime.fromtimestamp(context.last_activity).isoformat()
        }
    
    def _get_or_create_context(self, user_id: int) -> ConversationContext:
        """Get existing context or create new one"""
        if user_id not in self.conversation_contexts:
            self.conversation_contexts[user_id] = ConversationContext(
                user_id=user_id,
                messages=deque(maxlen=self.max_context_messages),
                topics=[],
                intent_history=[],
                preferences=self._load_user_preferences(user_id),
                last_activity=time.time(),
                session_start=time.time(),
                command_frequency=defaultdict(int)
            )
        
        return self.conversation_contexts[user_id]
    
    def _update_context(self, context: ConversationContext, message: str, command: Optional[str]):
        """Update conversation context with new message"""
        context.messages.append({
            "text": message,
            "timestamp": time.time(),
            "command": command
        })
        
        context.last_activity = time.time()
        
        if command:
            context.command_frequency[command] += 1
        
        # Extract topics from message
        new_topics = self._extract_topics(message)
        for topic in new_topics:
            if topic not in context.topics:
                context.topics.append(topic)
        
        # Limit topics to prevent memory bloat
        context.topics = context.topics[-10:]
    
    async def _analyze_intent(self, message: str, context: ConversationContext) -> UserIntent:
        """Analyze user intent from message and context"""
        message_lower = message.lower()
        
        # Check for explicit command patterns
        for pattern, intent_type in self.intent_patterns.items():
            if pattern in message_lower:
                return UserIntent(
                    intent_type=intent_type,
                    confidence=0.9,
                    entities=self._extract_entities(message, intent_type),
                    suggested_actions=self._get_suggested_actions(intent_type, context)
                )
        
        # Use AI for complex intent analysis
        try:
            ai_prompt = self._build_intent_analysis_prompt(message, context)
            ai_response = await get_ai_response(ai_prompt)
            
            # Parse AI response for intent
            intent_data = self._parse_ai_intent_response(ai_response)
            
            return UserIntent(
                intent_type=intent_data.get("intent", "general"),
                confidence=intent_data.get("confidence", 0.5),
                entities=intent_data.get("entities", {}),
                suggested_actions=self._get_suggested_actions(intent_data.get("intent", "general"), context)
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze intent with AI: {e}")
            
            # Fallback to simple classification
            return UserIntent(
                intent_type="general",
                confidence=0.3,
                entities={},
                suggested_actions=[]
            )
    
    async def _generate_contextual_response(self, message: str, context: ConversationContext, intent: UserIntent) -> Dict[str, Any]:
        """Generate contextual response using AI with conversation history"""
        try:
            # Build context-aware prompt
            prompt = self._build_contextual_prompt(message, context, intent)
            
            # Get AI response
            ai_response = await get_ai_response(prompt)
            
            # Generate suggestions based on context
            suggestions = await self._generate_suggestions(context, intent)
            
            return {
                "response": ai_response,
                "suggestions": suggestions
            }
            
        except Exception as e:
            logger.error(f"Failed to generate contextual response: {e}")
            return {
                "response": "I understand your message. How can I help you further?",
                "suggestions": []
            }
    
    def _build_contextual_prompt(self, message: str, context: ConversationContext, intent: UserIntent) -> str:
        """Build AI prompt with conversation context"""
        prompt = "You are Möbius, an advanced AI assistant for crypto research and productivity.\n\n"
        
        # Add user context
        if context.topics:
            prompt += f"Recent conversation topics: {', '.join(context.topics[-5:])}\n"
        
        if context.command_frequency:
            top_commands = sorted(context.command_frequency.items(), key=lambda x: x[1], reverse=True)[:3]
            prompt += f"User's frequently used commands: {', '.join([cmd for cmd, _ in top_commands])}\n"
        
        # Add intent context
        prompt += f"Detected user intent: {intent.intent_type} (confidence: {intent.confidence:.2f})\n"
        
        if intent.entities:
            prompt += f"Extracted entities: {intent.entities}\n"
        
        # Add recent conversation history
        if len(context.messages) > 1:
            prompt += "\nRecent conversation:\n"
            for msg in list(context.messages)[-3:]:  # Last 3 messages
                prompt += f"- {msg['text']}\n"
        
        prompt += f"\nCurrent message: {message}\n\n"
        prompt += "Provide a helpful, contextual response that acknowledges the conversation history and user's patterns. Be concise but informative."
        
        return prompt
    
    async def _generate_suggestions(self, context: ConversationContext, intent: UserIntent) -> List[str]:
        """Generate contextual suggestions for the user"""
        suggestions = []
        
        # Add intent-based suggestions
        suggestions.extend(intent.suggested_actions)
        
        # Add predictive suggestions
        predictions = await self.predict_user_needs(context.user_id)
        suggestions.extend(predictions)
        
        # Add context-based suggestions
        if "crypto" in context.topics:
            if "alert" not in [msg.get("command") for msg in context.messages]:
                suggestions.append("💡 Set up wallet alerts to monitor important addresses")
        
        if len(context.command_frequency) < 3:
            suggestions.append("❓ Try `/help` to discover more features")
        
        # Remove duplicates and limit
        unique_suggestions = []
        for suggestion in suggestions:
            if suggestion not in unique_suggestions:
                unique_suggestions.append(suggestion)
        
        return unique_suggestions[:5]
    
    def _extract_topics(self, message: str) -> List[str]:
        """Extract topics from message using keyword matching"""
        message_lower = message.lower()
        topics = []
        
        for topic, keywords in self.topic_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                topics.append(topic)
        
        return topics
    
    def _extract_entities(self, message: str, intent_type: str) -> Dict[str, Any]:
        """Extract entities based on intent type"""
        entities = {}
        message_lower = message.lower()
        
        # Extract wallet addresses (simplified)
        if "wallet" in intent_type or "address" in intent_type:
            import re
            eth_pattern = r'0x[a-fA-F0-9]{40}'
            addresses = re.findall(eth_pattern, message)
            if addresses:
                entities["addresses"] = addresses
        
        # Extract amounts
        if "alert" in intent_type or "transaction" in intent_type:
            import re
            amount_pattern = r'\$?(\d+(?:,\d{3})*(?:\.\d{2})?)'
            amounts = re.findall(amount_pattern, message)
            if amounts:
                entities["amounts"] = [float(amount.replace(',', '')) for amount in amounts]
        
        # Extract protocol names
        if "defi" in intent_type or "protocol" in intent_type:
            protocols = ["uniswap", "aave", "compound", "makerdao", "lido", "curve"]
            found_protocols = [p for p in protocols if p in message_lower]
            if found_protocols:
                entities["protocols"] = found_protocols
        
        return entities
    
    def _get_suggested_actions(self, intent_type: str, context: ConversationContext) -> List[str]:
        """Get suggested actions based on intent type"""
        suggestions = []
        
        action_map = {
            "crypto_research": [
                "🔍 Use `/arkham` to research wallet addresses",
                "📊 Check protocol data with `/llama`",
                "🏷️ Get wallet labels with `/nansen`"
            ],
            "wallet_management": [
                "💰 Create a new wallet with `/create_wallet`",
                "⚠️ Set up alerts with `/alert`",
                "📊 Check wallet analytics"
            ],
            "scheduling": [
                "📅 Set your Calendly link with `/set_calendly`",
                "🤝 Find someone's calendar with `/schedule`"
            ],
            "help": [
                "❓ Use `/help` for command list",
                "⭐ Check subscription with `/premium`",
                "📋 Get summary with `/summarynow`"
            ]
        }
        
        return action_map.get(intent_type, [])
    
    def _load_intent_patterns(self) -> Dict[str, str]:
        """Load intent recognition patterns"""
        return {
            "wallet": "wallet_management",
            "address": "wallet_management", 
            "balance": "wallet_management",
            "transaction": "wallet_management",
            "alert": "wallet_management",
            "defi": "crypto_research",
            "protocol": "crypto_research",
            "tvl": "crypto_research",
            "revenue": "crypto_research",
            "arkham": "crypto_research",
            "nansen": "crypto_research",
            "schedule": "scheduling",
            "calendar": "scheduling",
            "calendly": "scheduling",
            "meeting": "scheduling",
            "help": "help",
            "command": "help",
            "how": "help",
            "what": "help"
        }
    
    def _load_topic_keywords(self) -> Dict[str, List[str]]:
        """Load topic classification keywords"""
        return {
            "crypto": ["crypto", "cryptocurrency", "bitcoin", "ethereum", "defi", "nft"],
            "defi": ["defi", "protocol", "tvl", "yield", "liquidity", "staking"],
            "trading": ["trade", "buy", "sell", "price", "market", "exchange"],
            "wallet": ["wallet", "address", "balance", "transaction", "transfer"],
            "scheduling": ["schedule", "meeting", "calendar", "calendly", "appointment"],
            "analytics": ["data", "analytics", "metrics", "stats", "report"]
        }
    
    def _load_user_preferences(self, user_id: int) -> Dict[str, Any]:
        """Load user preferences from database"""
        try:
            preferences_json = enhanced_db.get_user_property(user_id, "ai_preferences", "{}")
            return json.loads(preferences_json)
        except:
            return {
                "response_style": "detailed",
                "preferred_topics": [],
                "notification_preferences": {}
            }
    
    def _update_user_preferences(self, context: ConversationContext, intent: UserIntent, command: Optional[str]):
        """Update user preferences based on interaction patterns"""
        # Update preferred topics
        if intent.intent_type not in context.preferences.get("preferred_topics", []):
            if "preferred_topics" not in context.preferences:
                context.preferences["preferred_topics"] = []
            context.preferences["preferred_topics"].append(intent.intent_type)
            context.preferences["preferred_topics"] = context.preferences["preferred_topics"][-5:]  # Keep last 5
        
        # Save to database periodically
        if len(context.messages) % 10 == 0:  # Every 10 messages
            try:
                enhanced_db.set_user_property(
                    context.user_id, 
                    "ai_preferences", 
                    json.dumps(context.preferences)
                )
            except Exception as e:
                logger.error(f"Failed to save user preferences: {e}")
    
    def _get_context_summary(self, context: ConversationContext) -> Dict[str, Any]:
        """Get summary of current conversation context"""
        return {
            "session_duration_minutes": (time.time() - context.session_start) / 60,
            "message_count": len(context.messages),
            "topics": context.topics[-5:],  # Last 5 topics
            "command_count": sum(context.command_frequency.values()),
            "most_used_command": max(context.command_frequency.items(), key=lambda x: x[1])[0] if context.command_frequency else None
        }
    
    def _parse_ai_intent_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response for intent classification"""
        # Simple parsing - in production, this would be more sophisticated
        response_lower = response.lower()
        
        intent_keywords = {
            "crypto_research": ["research", "analyze", "data", "protocol"],
            "wallet_management": ["wallet", "address", "transaction", "balance"],
            "scheduling": ["schedule", "meeting", "calendar"],
            "help": ["help", "assist", "guide", "explain"]
        }
        
        for intent, keywords in intent_keywords.items():
            if any(keyword in response_lower for keyword in keywords):
                return {
                    "intent": intent,
                    "confidence": 0.7,
                    "entities": {}
                }
        
        return {
            "intent": "general",
            "confidence": 0.5,
            "entities": {}
        }
    
    def _get_default_help(self) -> str:
        """Get default help text for new users"""
        return """
🎯 **Hey i'm Möbius mini and here are some quick commands to get you started:**

**🔍 Crypto Research:**
• `/llama <type> <slug>` - Get DeFi protocol data
• `/arkham <query>` - Research wallet addresses
• `/nansen <address>` - Get wallet labels

**💰 Wallet Management:**
• `/create_wallet` - Generate secure wallets
• `/alert <address> <amount>` - Set transaction alerts

**📅 Productivity:**
• `/set_calendly <link>` - Share your calendar
• `/schedule @user` - Find someone's calendar

**ℹ️ General:**
• `/help` - Show all commands
• `/premium` - Check subscription
• `/summarynow` - Get conversation summary

Start with any command to begin!
        """.strip()
    
    async def _periodic_cleanup(self):
        """Periodically clean up old conversation contexts"""
        while True:
            try:
                await asyncio.sleep(self.memory_cleanup_interval)
                
                current_time = time.time()
                expired_users = []
                
                for user_id, context in self.conversation_contexts.items():
                    if current_time - context.last_activity > self.context_timeout:
                        expired_users.append(user_id)
                
                for user_id in expired_users:
                    del self.conversation_contexts[user_id]
                
                if expired_users:
                    logger.info(f"Cleaned up {len(expired_users)} expired conversation contexts")
                    
            except Exception as e:
                logger.error(f"Error in context cleanup: {e}")

# Global contextual AI instance
contextual_ai = ContextualAI()