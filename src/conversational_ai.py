# src/conversational_ai.py
"""
Advanced Conversational AI Engine for Möbius
Handles natural conversations, context awareness, and intelligent task routing
"""

import logging
import re
import json
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

try:
    from persistent_user_context import user_context_manager, ConversationContext
except ImportError:
    ConversationContext = None
    user_context_manager = None

try:
    from command_intent_mapper import map_natural_language_to_command
except ImportError:
    def map_natural_language_to_command(*args, **kwargs):
        return None

logger = logging.getLogger(__name__)

class ConversationType(Enum):
    """Types of conversations"""
    CASUAL = "casual"
    TASK_ORIENTED = "task_oriented"
    INFORMATION_SEEKING = "information_seeking"
    PROBLEM_SOLVING = "problem_solving"
    SOCIAL = "social"

class ResponseType(Enum):
    """Types of responses"""
    CONVERSATIONAL = "conversational"
    TASK_EXECUTION = "task_execution"
    INFORMATION_DELIVERY = "information_delivery"
    CLARIFICATION = "clarification"
    EMPATHETIC = "empathetic"

@dataclass
class ConversationState:
    """Current conversation state"""
    user_id: int
    conversation_type: ConversationType = ConversationType.CASUAL
    active_topic: Optional[str] = None
    pending_tasks: List[str] = field(default_factory=list)
    context_memory: List[Dict[str, Any]] = field(default_factory=list)
    user_mood: Optional[str] = None
    conversation_depth: int = 0
    last_interaction: Optional[datetime] = None

class ConversationalAI:
    """Advanced conversational AI engine"""
    
    def __init__(self):
        self.conversation_states: Dict[int, ConversationState] = {}
        self.personality_traits = {
            "helpful": 0.9,
            "friendly": 0.8,
            "professional": 0.7,
            "empathetic": 0.8,
            "knowledgeable": 0.9,
            "patient": 0.9
        }
        
        # Conversation patterns
        self.greeting_patterns = [
            r"^(hi|hello|hey|good morning|good afternoon|good evening|greetings)",
            r"(what'?s up|how are you|how'?s it going|how are things)",
            r"(yo|sup|howdy|hiya)"
        ]
        
        self.farewell_patterns = [
            r"(bye|goodbye|see you|talk to you later|ttyl|cya|farewell)",
            r"(good night|gn|sleep well|take care)",
            r"(thanks.*bye|thank you.*goodbye)"
        ]
        
        self.question_patterns = [
            r"(what|how|why|when|where|who|which|can you|could you|would you)",
            r"(tell me|show me|explain|describe|help me understand)",
            r"(is it|are you|do you|did you|will you|have you)"
        ]
        
        self.task_patterns = [
            r"(check|get|find|search|look up|analyze|research|monitor)",
            r"(set.*alert|create.*alert|notify me|remind me)",
            r"(show.*portfolio|track.*price|watch.*market)",
            r"(summarize|recap|overview|digest)",
            r"(what'?s.*?(tvl|price|volume|market cap))",
            r"(show.*?(tvl|defi|protocol|trending))",
            r"(tell me.*?(about|tvl|price|data))",
            r"(give me.*?(summary|data|info|price))"
        ]
        
        self.emotional_patterns = {
            "excited": [r"(amazing|awesome|fantastic|great|excellent|love it|perfect)"],
            "frustrated": [r"(annoying|frustrated|angry|mad|upset|terrible|awful)"],
            "confused": [r"(confused|don'?t understand|unclear|lost|help|what do you mean)"],
            "grateful": [r"(thank you|thanks|appreciate|grateful|helpful)"],
            "curious": [r"(interesting|curious|wonder|tell me more|how does|why does)"]
        }
        
    async def process_conversation(self, user_id: int, text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process conversational input and generate appropriate response"""
        
        # Get or create conversation state
        conv_state = self._get_conversation_state(user_id)
        
        # Update conversation context
        await self._update_conversation_context(conv_state, text, context)
        
        # Analyze conversation type and intent
        conversation_analysis = await self._analyze_conversation(text, conv_state)
        
        # Determine response strategy
        response_strategy = await self._determine_response_strategy(
            text, conversation_analysis, conv_state, context
        )
        
        # Generate response
        response = await self._generate_contextual_response(
            text, response_strategy, conv_state, context
        )
        
        # Update conversation state
        await self._update_conversation_state(conv_state, text, response)
        
        return response
    
    def _get_conversation_state(self, user_id: int) -> ConversationState:
        """Get or create conversation state for user"""
        if user_id not in self.conversation_states:
            self.conversation_states[user_id] = ConversationState(user_id=user_id)
        
        state = self.conversation_states[user_id]
        
        # Reset if conversation is stale (>30 minutes)
        if (state.last_interaction and 
            datetime.now() - state.last_interaction > timedelta(minutes=30)):
            self.conversation_states[user_id] = ConversationState(user_id=user_id)
            state = self.conversation_states[user_id]
        
        return state
    
    async def _update_conversation_context(self, state: ConversationState, text: str, context: Dict[str, Any]):
        """Update conversation context with new message"""
        
        # Add to context memory
        state.context_memory.append({
            "timestamp": datetime.now().isoformat(),
            "text": text,
            "context": context,
            "type": "user_message"
        })
        
        # Limit context memory
        if len(state.context_memory) > 20:
            state.context_memory = state.context_memory[-20:]
        
        state.last_interaction = datetime.now()
        state.conversation_depth += 1
    
    async def _analyze_conversation(self, text: str, state: ConversationState) -> Dict[str, Any]:
        """Analyze conversation type, mood, and intent"""
        
        text_lower = text.lower()
        analysis = {
            "conversation_type": ConversationType.CASUAL,
            "is_greeting": False,
            "is_farewell": False,
            "is_question": False,
            "is_task_request": False,
            "emotional_tone": None,
            "topics": [],
            "entities": []
        }
        
        # Check for greetings
        for pattern in self.greeting_patterns:
            if re.search(pattern, text_lower):
                analysis["is_greeting"] = True
                analysis["conversation_type"] = ConversationType.SOCIAL
                break
        
        # Check for farewells
        for pattern in self.farewell_patterns:
            if re.search(pattern, text_lower):
                analysis["is_farewell"] = True
                analysis["conversation_type"] = ConversationType.SOCIAL
                break
        
        # Check for questions
        for pattern in self.question_patterns:
            if re.search(pattern, text_lower):
                analysis["is_question"] = True
                analysis["conversation_type"] = ConversationType.INFORMATION_SEEKING
                break
        
        # Check for task requests
        for pattern in self.task_patterns:
            if re.search(pattern, text_lower):
                analysis["is_task_request"] = True
                analysis["conversation_type"] = ConversationType.TASK_ORIENTED
                break
        
        # Detect emotional tone
        for emotion, patterns in self.emotional_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    analysis["emotional_tone"] = emotion
                    break
            if analysis["emotional_tone"]:
                break
        
        # Extract crypto/finance topics
        crypto_topics = re.findall(
            r'\b(bitcoin|btc|ethereum|eth|solana|sol|cardano|ada|polkadot|dot|'
            r'chainlink|link|uniswap|uni|aave|compound|makerdao|defi|nft|'
            r'yield farming|staking|liquidity|trading|portfolio|market|price)\b',
            text_lower
        )
        analysis["topics"] = list(set(crypto_topics))
        
        return analysis
    
    async def _determine_response_strategy(
        self, 
        text: str, 
        analysis: Dict[str, Any], 
        state: ConversationState,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Determine the best response strategy"""
        
        strategy = {
            "response_type": ResponseType.CONVERSATIONAL,
            "should_execute_task": False,
            "should_ask_clarification": False,
            "personality_emphasis": ["helpful", "friendly"],
            "conversation_flow": "continue"
        }
        
        # Handle greetings
        if analysis["is_greeting"]:
            strategy["response_type"] = ResponseType.CONVERSATIONAL
            strategy["personality_emphasis"] = ["friendly", "welcoming"]
            strategy["conversation_flow"] = "greeting"
        
        # Handle farewells
        elif analysis["is_farewell"]:
            strategy["response_type"] = ResponseType.CONVERSATIONAL
            strategy["personality_emphasis"] = ["friendly", "caring"]
            strategy["conversation_flow"] = "farewell"
        
        # Handle task requests
        elif analysis["is_task_request"]:
            strategy["response_type"] = ResponseType.TASK_EXECUTION
            strategy["should_execute_task"] = True
            strategy["personality_emphasis"] = ["helpful", "efficient"]
        
        # Handle questions
        elif analysis["is_question"]:
            if analysis["topics"]:
                strategy["response_type"] = ResponseType.INFORMATION_DELIVERY
                strategy["personality_emphasis"] = ["knowledgeable", "helpful"]
            else:
                strategy["response_type"] = ResponseType.CONVERSATIONAL
                strategy["personality_emphasis"] = ["helpful", "patient"]
        
        # Handle emotional responses
        if analysis["emotional_tone"]:
            if analysis["emotional_tone"] in ["frustrated", "confused"]:
                strategy["personality_emphasis"] = ["empathetic", "patient", "helpful"]
                strategy["should_ask_clarification"] = True
            elif analysis["emotional_tone"] in ["excited", "grateful"]:
                strategy["personality_emphasis"] = ["friendly", "enthusiastic"]
        
        return strategy
    
    async def _generate_contextual_response(
        self,
        text: str,
        strategy: Dict[str, Any],
        state: ConversationState,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate contextual response based on strategy"""
        
        response_type = strategy["response_type"]
        flow = strategy["conversation_flow"]
        
        # Handle different response types
        if response_type == ResponseType.CONVERSATIONAL:
            return await self._generate_conversational_response(text, strategy, state, context)
        
        elif response_type == ResponseType.TASK_EXECUTION:
            return await self._generate_task_response(text, strategy, state, context)
        
        elif response_type == ResponseType.INFORMATION_DELIVERY:
            return await self._generate_information_response(text, strategy, state, context)
        
        elif response_type == ResponseType.CLARIFICATION:
            return await self._generate_clarification_response(text, strategy, state, context)
        
        else:
            return await self._generate_fallback_response(text, strategy, state, context)
    
    async def _generate_conversational_response(
        self, text: str, strategy: Dict[str, Any], state: ConversationState, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate natural conversational response"""
        
        flow = strategy.get("conversation_flow", "continue")
        username = context.get("username", "friend")
        
        if flow == "greeting":
            responses = [
                f"Hey {username}! 👋 Great to see you! How can I help you today?",
                f"Hello {username}! 🤖 I'm here and ready to assist. What's on your mind?",
                f"Hi there {username}! ✨ Hope you're having a good day. What can I do for you?",
                f"Hey {username}! 🚀 Ready to dive into some crypto talk or need help with something?"
            ]
            
            # Add context-aware greetings
            if state.conversation_depth > 1:
                responses.extend([
                    f"Welcome back {username}! 😊 Continuing our conversation...",
                    f"Good to see you again {username}! 🔄 What's next?"
                ])
        
        elif flow == "farewell":
            responses = [
                f"Take care {username}! 👋 Feel free to come back anytime you need help.",
                f"Goodbye {username}! 🌟 It was great chatting with you. See you soon!",
                f"Until next time {username}! 🚀 Happy trading and stay safe out there!",
                f"Bye {username}! 💫 Remember, I'm always here when you need crypto insights."
            ]
        
        else:
            # Contextual conversational responses
            if "thank" in text.lower():
                responses = [
                    "You're very welcome! 😊 Always happy to help.",
                    "My pleasure! 🤖 That's what I'm here for.",
                    "Glad I could help! ✨ Anything else you need?",
                    "No problem at all! 🚀 Feel free to ask me anything else."
                ]
            
            elif any(word in text.lower() for word in ["how are you", "how's it going"]):
                responses = [
                    "I'm doing great, thanks for asking! 🤖 Ready to help with all things crypto. How about you?",
                    "Fantastic! 🚀 I've been busy analyzing markets and helping users. What brings you here today?",
                    "I'm excellent! ✨ Always excited to chat about crypto and help out. How are you doing?",
                    "Wonderful! 💫 Just finished processing some market data. What can I help you with?"
                ]
            
            elif "what can you do" in text.lower() or "capabilities" in text.lower():
                responses = [
                    "I'm your crypto companion! 🤖 I can check prices, analyze portfolios, set alerts, research projects, and have natural conversations about anything crypto-related. What interests you most?",
                    "Lots of things! 🚀 Price tracking, portfolio analysis, market research, setting up alerts, and just chatting about crypto trends. I'm also great at explaining complex DeFi concepts. What would you like to explore?",
                    "I'm here to make crypto easier for you! ✨ From real-time price data to deep protocol research, portfolio tracking to social sentiment analysis. Plus, I love having conversations about the space. What's your focus today?"
                ]
            
            else:
                # General conversational responses
                responses = [
                    "That's interesting! 🤔 Tell me more about what you're thinking.",
                    "I hear you! 💭 What would you like to explore further?",
                    "Absolutely! 🚀 I'm here to help however I can.",
                    "I understand! ✨ What specific aspect interests you most?",
                    "Great point! 💫 How can I assist you with that?"
                ]
        
        import random
        selected_response = random.choice(responses)
        
        return {
            "type": "conversational",
            "message": selected_response,
            "conversation_type": "natural",
            "follow_up_suggestions": self._get_follow_up_suggestions(text, state)
        }
    
    async def _generate_task_response(
        self, text: str, strategy: Dict[str, Any], state: ConversationState, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate task-oriented response"""
        
        # Try to map to specific command
        command_mapping = map_natural_language_to_command("task", text, 0.8)
        
        if command_mapping:
            command, parameters = command_mapping
            return {
                "type": "task_execution",
                "message": f"🚀 I'll help you with that! Let me {command.replace('_', ' ')}...",
                "command": command,
                "parameters": parameters,
                "conversation_context": True
            }
        
        # Generic task acknowledgment
        return {
            "type": "task_acknowledgment",
            "message": "🤖 I understand you need help with a task. Let me see what I can do for you...",
            "requires_clarification": True,
            "suggestions": [
                "Check crypto prices",
                "Analyze portfolio",
                "Set price alerts",
                "Research projects"
            ]
        }
    
    async def _generate_information_response(
        self, text: str, strategy: Dict[str, Any], state: ConversationState, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate information-focused response"""
        
        return {
            "type": "information_seeking",
            "message": "🧠 Great question! Let me gather the latest information for you...",
            "requires_data_fetch": True,
            "conversation_context": True
        }
    
    async def _generate_clarification_response(
        self, text: str, strategy: Dict[str, Any], state: ConversationState, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate clarification response"""
        
        return {
            "type": "clarification",
            "message": "🤔 I want to make sure I understand correctly. Could you help me clarify what you're looking for?",
            "clarification_questions": [
                "Are you looking for price information?",
                "Do you need help with portfolio tracking?",
                "Would you like to set up alerts?",
                "Are you interested in project research?"
            ]
        }
    
    async def _generate_fallback_response(
        self, text: str, strategy: Dict[str, Any], state: ConversationState, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate fallback response"""
        
        return {
            "type": "conversational",
            "message": "🤖 I'm here to help! Could you tell me a bit more about what you're looking for? I'm great with crypto prices, portfolio analysis, research, and general crypto conversations.",
            "suggestions": [
                "Ask about crypto prices",
                "Check portfolio performance", 
                "Research DeFi projects",
                "Set up price alerts",
                "Get market analysis"
            ]
        }
    
    def _get_follow_up_suggestions(self, text: str, state: ConversationState) -> List[str]:
        """Get contextual follow-up suggestions"""
        
        suggestions = []
        
        # Based on conversation history
        if state.active_topic:
            suggestions.append(f"Tell me more about {state.active_topic}")
        
        # Based on current text
        if any(word in text.lower() for word in ["price", "cost", "value"]):
            suggestions.extend([
                "Set a price alert",
                "Check portfolio performance",
                "Compare with other assets"
            ])
        
        elif any(word in text.lower() for word in ["portfolio", "holdings", "balance"]):
            suggestions.extend([
                "Analyze portfolio risk",
                "Track performance",
                "Rebalancing suggestions"
            ])
        
        # Default suggestions
        if not suggestions:
            suggestions = [
                "Check latest crypto prices",
                "Research trending projects", 
                "Set up alerts",
                "Analyze market trends"
            ]
        
        return suggestions[:3]  # Limit to 3 suggestions
    
    async def _update_conversation_state(
        self, state: ConversationState, user_text: str, response: Dict[str, Any]
    ):
        """Update conversation state after response"""
        
        # Add response to context memory
        state.context_memory.append({
            "timestamp": datetime.now().isoformat(),
            "text": response.get("message", ""),
            "type": "bot_response",
            "response_type": response.get("type", "unknown")
        })
        
        # Update active topic if detected
        if "topics" in response:
            topics = response["topics"]
            if topics:
                state.active_topic = topics[0]
        
        # Update conversation type
        if response.get("type") == "task_execution":
            state.conversation_type = ConversationType.TASK_ORIENTED
        elif response.get("type") == "information_seeking":
            state.conversation_type = ConversationType.INFORMATION_SEEKING

# Global instance
conversational_ai = ConversationalAI()

async def process_conversational_input(user_id: int, text: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Main function to process conversational input"""
    return await conversational_ai.process_conversation(user_id, text, context)