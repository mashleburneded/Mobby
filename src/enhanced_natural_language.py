# src/enhanced_natural_language.py
"""
Enhanced Natural Language Processing Engine for Möbius AI Assistant
Provides intelligent intent recognition, context-aware responses, and seamless command routing
"""

import asyncio
import logging
import re
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import aiohttp
from config import config
from persistent_user_context import user_context_manager, ConversationContext
from intelligent_error_handler import error_handler

# Set up logger first
logger = logging.getLogger(__name__)

try:
    from mcp_intent_router import route_user_request, analyze_user_intent
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    logger.warning("MCP modules not available, using fallback mode")

from command_intent_mapper import map_natural_language_to_command, get_command_suggestions_for_intent
from conversational_ai import process_conversational_input

@dataclass
class ProcessingResult:
    """Result of natural language processing"""
    success: bool
    response: Dict[str, Any]
    intent: Optional[str] = None
    confidence: float = 0.0
    processing_time: float = 0.0
    fallback_response: Optional[str] = None

class EnhancedNaturalLanguageEngine:
    """Enhanced NLP engine with intelligent intent recognition and response generation"""
    
    def __init__(self):
        self.intent_patterns = self._initialize_intent_patterns()
        self.response_templates = self._initialize_response_templates()
        self.command_mappings = self._initialize_command_mappings()
        self.context_cache = {}
        self.rate_limiter = self._initialize_rate_limiter()
        
    def _initialize_intent_patterns(self) -> Dict[str, List[str]]:
        """Initialize comprehensive intent recognition patterns"""
        return {
            # Greeting and basic interaction
            "greeting": [
                r"^(hi|hello|hey|greetings|good\s+(morning|afternoon|evening))",
                r"^(what'?s up|how are you|how'?s it going)",
                r"^(start|begin|let'?s start)"
            ],
            
            # Help and information
            "help": [
                r"(help|assistance|support|guide|how to|tutorial)",
                r"(what can you do|capabilities|features|commands)",
                r"(explain|show me|tell me about)"
            ],
            
            # Price queries
            "price_query": [
                r"(price|cost|value|worth).*?(btc|bitcoin|eth|ethereum|\$\w+|\w+coin)",
                r"(how much|what'?s the price|current price|latest price)",
                r"(check price|get price|price of|show price)"
            ],
            
            # Portfolio management
            "portfolio": [
                r"(portfolio|holdings|balance|assets|investments)",
                r"(my (coins|tokens|crypto|investments))",
                r"(track|monitor|watch).*?(portfolio|holdings)"
            ],
            
            # Alerts and notifications
            "alerts": [
                r"(alert|notify|notification|remind).*?(when|if|price)",
                r"(set.*?alert|create.*?alert|add.*?alert)",
                r"(tell me when|let me know when|notify me when)"
            ],
            
            # Research and analysis
            "research": [
                r"(research|analyze|analysis|study|investigate)",
                r"(market.*?(analysis|research|data|trends))",
                r"(fundamental|technical).*?(analysis|research)"
            ],
            
            # Trading and DeFi
            "trading": [
                r"(trade|trading|buy|sell|swap|exchange)",
                r"(arbitrage|profit|opportunity)"
            ],
            
            # DeFi specific queries
            "defi": [
                r"(tvl|total.*?value.*?locked)",
                r"(defi|yield|farming|liquidity|staking)",
                r"(hyperliquid|uniswap|aave|compound|curve)",
                r"(protocol.*?(tvl|volume|fees))",
                r"(what'?s.*?tvl.*?of)",
                r"(show.*?(tvl|defi|protocol))"
            ],
            
            # News and updates
            "news": [
                r"(news|updates|latest|recent|happening)",
                r"(market.*?(news|updates|events))",
                r"(what'?s new|any news|latest updates)"
            ],
            
            # Complex queries requiring AI
            "ai_query": [
                r"(explain|describe|tell me about|what is|how does)",
                r"(compare|comparison|difference|versus|vs)",
                r"(predict|forecast|future|trend|outlook)"
            ]
        }
    
    def _initialize_response_templates(self) -> Dict[str, List[str]]:
        """Initialize response templates for different intents"""
        return {
            "greeting": [
                "👋 Hello! I'm Möbius, your AI crypto assistant. How can I help you today?",
                "🚀 Hey there! Ready to explore the crypto universe together?",
                "✨ Greetings! I'm here to help with all your crypto needs."
            ],
            
            "help": [
                "🤖 I can help you with:\n• Price tracking and alerts\n• Portfolio management\n• Market research\n• DeFi opportunities\n• Trading insights\n\nTry asking: 'What's the price of Bitcoin?' or 'Set an alert for ETH at $3000'",
                "💡 Here are some things you can ask me:\n• 'Check my portfolio'\n• 'Research Solana'\n• 'Alert me when BTC hits $100k'\n• 'What's happening in DeFi?'"
            ],
            
            "price_query": [
                "📊 Let me get the latest price data for you...",
                "💰 Fetching current market prices...",
                "📈 Checking the latest crypto prices..."
            ],
            
            "portfolio": [
                "📊 Let me analyze your portfolio...",
                "💼 Checking your holdings and performance...",
                "📈 Gathering your portfolio data..."
            ],
            
            "alerts": [
                "🔔 Setting up your price alert...",
                "⚡ Creating a smart alert for you...",
                "📢 I'll notify you when your conditions are met..."
            ],
            
            "research": [
                "🔍 Conducting comprehensive research...",
                "📊 Analyzing market data and trends...",
                "🧠 Gathering insights from multiple sources..."
            ],
            
            "defi": [
                "🏦 Fetching DeFi protocol data...",
                "💎 Analyzing TVL and DeFi metrics...",
                "🔗 Checking protocol statistics...",
                "📊 Getting the latest DeFi information..."
            ],
            
            "fallback": [
                "🤔 I'm not sure I understand. Could you rephrase that?",
                "💭 Let me think... Could you be more specific?",
                "🔄 I'm having trouble with that request. Try using a command like /help"
            ]
        }
    
    def _initialize_command_mappings(self) -> Dict[str, str]:
        """Map intents to specific commands"""
        return {
            "price_query": "price_command",
            "portfolio": "portfolio_command", 
            "alerts": "alert_command",
            "research": "research_command",
            "help": "help_command",
            "news": "news_command",
            "defi": "defi_command",
            "trading": "trading_command"
        }
    
    def _initialize_rate_limiter(self):
        """Initialize rate limiting for AI API calls"""
        return {
            "requests": [],
            "max_per_minute": 50,
            "max_per_hour": 500
        }
    
    async def process_natural_language(self, user_id: int, text: str, context: Dict[str, Any]) -> ProcessingResult:
        """Main entry point for natural language processing"""
        start_time = time.time()
        
        try:
            # Get user context
            user_context = await self._get_user_context(user_id)
            
            # Analyze intent
            intent_result = await self._analyze_intent(text, user_context, context)
            
            # Route to appropriate handler
            response = await self._route_request(intent_result, user_id, text, context)
            
            # Update user context
            await self._update_user_context(user_id, intent_result, text)
            
            processing_time = time.time() - start_time
            
            return ProcessingResult(
                success=True,
                response=response,
                intent=intent_result.get("intent"),
                confidence=intent_result.get("confidence", 0.0),
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Error in natural language processing: {e}")
            processing_time = time.time() - start_time
            
            return ProcessingResult(
                success=False,
                response={
                    "type": "error",
                    "message": "❌ I'm having trouble processing that request. Please try again."
                },
                processing_time=processing_time,
                fallback_response="I'm having trouble understanding. Could you rephrase that?"
            )
    
    async def _get_user_context(self, user_id: int) -> ConversationContext:
        """Get or create user context"""
        try:
            return user_context_manager.get_user_context(user_id)
        except Exception as e:
            logger.warning(f"Could not load user context for {user_id}: {e}")
            return ConversationContext(user_id=user_id)
    
    async def _analyze_intent(self, text: str, user_context: ConversationContext, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user intent using pattern matching and context"""
        text_lower = text.lower().strip()
        
        # Check for explicit commands first
        if text_lower.startswith('/'):
            return {
                "intent": "command",
                "confidence": 1.0,
                "command": text_lower.split()[0][1:],
                "strategy": "direct"
            }
        
        # Pattern-based intent recognition
        best_intent = None
        best_confidence = 0.0
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    confidence = self._calculate_confidence(pattern, text_lower, user_context)
                    if confidence > best_confidence:
                        best_intent = intent
                        best_confidence = confidence
        
        # Use MCP intent router for complex analysis
        if best_confidence < 0.7:
            try:
                mcp_result = await analyze_user_intent(text, context)
                if mcp_result and mcp_result.get("confidence", 0) > best_confidence:
                    return mcp_result
            except Exception as e:
                logger.warning(f"MCP intent analysis failed: {e}")
        
        # Fallback to simple intent
        if not best_intent:
            best_intent = "ai_query" if len(text_lower) > 10 else "simple"
            best_confidence = 0.5
        
        return {
            "intent": best_intent,
            "confidence": best_confidence,
            "strategy": "pattern_match",
            "entities": self._extract_entities(text)
        }
    
    def _calculate_confidence(self, pattern: str, text: str, user_context: ConversationContext) -> float:
        """Calculate confidence score for pattern match"""
        base_confidence = 0.8
        
        # Boost confidence based on context
        if user_context.last_intent and pattern in self.intent_patterns.get(user_context.last_intent, []):
            base_confidence += 0.1
        
        # Boost for exact matches
        if re.fullmatch(pattern, text):
            base_confidence += 0.2
        
        return min(base_confidence, 1.0)
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract entities from text"""
        entities = []
        
        # Crypto symbols
        crypto_pattern = r'\b(BTC|ETH|SOL|ADA|DOT|LINK|UNI|AAVE|MATIC|AVAX|ATOM|NEAR|FTM|ALGO|XRP|LTC|BCH|ETC|XLM|VET|THETA|TFUEL|HBAR|ICP|FIL|EOS|TRX|XTZ|DASH|ZEC|QTUM|ONT|ZIL|RVN|DGB|SC|DCR|LSK|ARDR|STRAT|WAVES|NXT|BURST|XEM|MONA|DOGE|SHIB)\b'
        entities.extend(re.findall(crypto_pattern, text.upper()))
        
        # Price values
        price_pattern = r'\$[\d,]+(?:\.\d{2})?'
        entities.extend(re.findall(price_pattern, text))
        
        # Percentages
        percent_pattern = r'\d+(?:\.\d+)?%'
        entities.extend(re.findall(percent_pattern, text))
        
        return entities
    
    async def _route_request(self, intent_result: Dict[str, Any], user_id: int, text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Route request to appropriate handler"""
        intent = intent_result.get("intent")
        confidence = intent_result.get("confidence", 0.0)
        
        # Try command mapping first
        command_mapping = map_natural_language_to_command(intent, text, confidence)
        if command_mapping:
            command, parameters = command_mapping
            return await self._execute_mapped_command(command, parameters, text, user_id, context)
        
        # High confidence intents - route to specific handlers
        if confidence > 0.7 and intent in self.command_mappings:
            return await self._handle_specific_intent(intent, text, user_id, context)
        
        # Medium confidence - use MCP routing
        elif confidence > 0.4 and MCP_AVAILABLE:
            try:
                mcp_result = await route_user_request(user_id, text, context)
                if mcp_result and mcp_result.get("success"):
                    return mcp_result["response"]
            except Exception as e:
                logger.warning(f"MCP routing failed: {e}")
        
        # Low confidence or fallback - use AI response
        return await self._generate_ai_response(text, user_id, context)
    
    async def _execute_mapped_command(self, command: str, parameters: Dict[str, Any], text: str, user_id: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a mapped command with extracted parameters"""
        
        # Build command arguments from parameters
        args = []
        if "symbol" in parameters:
            args.append(parameters["symbol"])
        elif "protocol" in parameters:
            args.append(parameters["protocol"])
        elif "price" in parameters:
            args.append(parameters["price"])
        
        # Format the command execution message
        if command == "research":
            if args:
                return {
                    "type": "background_processing",
                    "message": f"🔍 Researching {args[0]}...",
                    "command": command,
                    "params": {"query": " ".join(args)}
                }
            else:
                return {
                    "type": "background_processing",
                    "message": "🔍 Conducting market research...",
                    "command": command,
                    "params": {"query": text}
                }
        
        elif command == "alert":
            return {
                "type": "background_processing",
                "message": "🔔 Setting up your alert...",
                "command": command,
                "params": {"text": text, **parameters}
            }
        
        elif command == "portfolio":
            return {
                "type": "background_processing",
                "message": "📊 Analyzing your portfolio...",
                "command": command,
                "params": parameters
            }
        
        elif command == "status":
            return {
                "type": "immediate_response",
                "message": "🤖 Checking system status...",
                "command": command,
                "params": {}
            }
        
        elif command == "help":
            return {
                "type": "help",
                "message": "🤖 Here's how I can help you:",
                "suggestions": get_command_suggestions_for_intent("help")
            }
        
        elif command == "menu":
            return {
                "type": "menu",
                "message": "📋 Main Menu - Choose an option:",
                "suggestions": [
                    "Check prices",
                    "View portfolio", 
                    "Set alerts",
                    "Research projects",
                    "Get help"
                ]
            }
        
        else:
            # Generic command execution
            return {
                "type": "background_processing",
                "message": f"⚡ Executing {command}...",
                "command": command,
                "params": parameters
            }
    
    async def _handle_specific_intent(self, intent: str, text: str, user_id: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle specific intents with targeted responses"""
        
        if intent == "greeting":
            return {
                "type": "greeting",
                "message": self._get_random_response("greeting"),
                "suggestions": [
                    "Check Bitcoin price",
                    "Set up price alerts", 
                    "Research trending coins",
                    "View my portfolio"
                ]
            }
        
        elif intent == "help":
            return {
                "type": "help",
                "message": self._get_random_response("help"),
                "suggestions": [
                    "/menu - Show all commands",
                    "/price BTC - Get Bitcoin price",
                    "/portfolio - View portfolio",
                    "/alerts - Manage alerts"
                ]
            }
        
        elif intent == "price_query":
            # Extract crypto symbol
            entities = self._extract_entities(text)
            symbol = entities[0] if entities else "BTC"
            
            return {
                "type": "background_processing",
                "message": f"📊 Getting latest {symbol} price data...",
                "command": "price",
                "params": {"symbol": symbol}
            }
        
        elif intent == "portfolio":
            return {
                "type": "background_processing", 
                "message": "📊 Analyzing your portfolio...",
                "command": "portfolio",
                "params": {}
            }
        
        elif intent == "alerts":
            return {
                "type": "background_processing",
                "message": "🔔 Setting up your alert...",
                "command": "alert",
                "params": {"text": text}
            }
        
        elif intent == "research":
            entities = self._extract_entities(text)
            topic = entities[0] if entities else "market"
            
            return {
                "type": "background_processing",
                "message": f"🔍 Researching {topic}...",
                "command": "research",
                "params": {"topic": topic, "query": text}
            }
        
        else:
            return await self._generate_ai_response(text, user_id, context)
    
    async def _generate_ai_response(self, text: str, user_id: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI response using Groq or fallback"""
        try:
            # Check rate limits
            if not self._check_rate_limit():
                return {
                    "type": "ai_response",
                    "message": "🤔 I'm processing a lot of requests right now. Please try again in a moment."
                }
            
            # Use AI provider for intelligent response
            try:
                from ai_providers import get_ai_response
            except ImportError:
                logger.warning("AI providers not available, using fallback response")
                return {
                    "type": "fallback",
                    "message": "I'm having trouble accessing my AI capabilities right now. Please try a specific command like /help or /menu."
                }
            
            ai_prompt = f"""You are Möbius, an intelligent crypto AI assistant. 
            
User query: {text}
Context: {context.get('chat_type', 'private')} chat

Provide a helpful, concise response. If the user is asking about:
- Prices: Suggest using specific commands like /price BTC
- Portfolio: Suggest /portfolio command  
- Alerts: Suggest /alert command
- Research: Provide brief insights and suggest /research command

Keep responses under 200 words and be friendly but professional."""

            ai_response = await get_ai_response(ai_prompt, user_id)
            
            return {
                "type": "ai_response",
                "message": ai_response,
                "suggestions": self._generate_suggestions(text)
            }
            
        except Exception as e:
            logger.error(f"AI response generation failed: {e}")
            return {
                "type": "fallback",
                "message": self._get_random_response("fallback")
            }
    
    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits"""
        now = time.time()
        
        # Clean old requests
        self.rate_limiter["requests"] = [
            req_time for req_time in self.rate_limiter["requests"]
            if now - req_time < 3600  # Keep last hour
        ]
        
        # Check limits
        recent_requests = [
            req_time for req_time in self.rate_limiter["requests"]
            if now - req_time < 60  # Last minute
        ]
        
        if len(recent_requests) >= self.rate_limiter["max_per_minute"]:
            return False
        
        if len(self.rate_limiter["requests"]) >= self.rate_limiter["max_per_hour"]:
            return False
        
        # Add current request
        self.rate_limiter["requests"].append(now)
        return True
    
    def _get_random_response(self, intent: str) -> str:
        """Get a random response template for the intent"""
        templates = self.response_templates.get(intent, self.response_templates["fallback"])
        import random
        return random.choice(templates)
    
    def _generate_suggestions(self, text: str) -> List[str]:
        """Generate contextual suggestions based on user input"""
        suggestions = []
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["price", "cost", "value"]):
            suggestions.extend([
                "Set price alerts",
                "View price charts", 
                "Compare prices"
            ])
        
        if any(word in text_lower for word in ["portfolio", "holdings"]):
            suggestions.extend([
                "Analyze performance",
                "Rebalance portfolio",
                "Track profits"
            ])
        
        if any(word in text_lower for word in ["research", "analyze"]):
            suggestions.extend([
                "Get market insights",
                "Check social sentiment",
                "View technical analysis"
            ])
        
        # Default suggestions
        if not suggestions:
            suggestions = [
                "Check Bitcoin price",
                "Set up alerts",
                "Research trending coins"
            ]
        
        return suggestions[:3]  # Limit to 3 suggestions
    
    async def _update_user_context(self, user_id: int, intent_result: Dict[str, Any], text: str):
        """Update user context with latest interaction"""
        try:
            user_context_manager.update_conversation_flow(
                user_id,
                "user_message",
                text,
                intent_result.get("intent")
            )
        except Exception as e:
            logger.warning(f"Failed to update user context: {e}")

# Global instance
enhanced_nlp_engine = EnhancedNaturalLanguageEngine()

# Main processing function
async def process_natural_language(user_id: int, text: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Main entry point for natural language processing with conversational AI"""
    try:
        # First, try conversational AI for natural interaction
        conversational_response = await process_conversational_input(user_id, text, context)
        
        # If it's a pure conversational response, return it
        if conversational_response.get("type") == "conversational":
            return {
                "success": True,
                "response": conversational_response,
                "intent": "conversation",
                "confidence": 0.9,
                "processing_time": 0.1,
                "fallback_response": None
            }
        
        # If it requires task execution, continue with NLP engine
        elif conversational_response.get("type") in ["task_execution", "task_acknowledgment", "information_seeking"]:
            # Use the enhanced NLP engine for task processing
            result = await enhanced_nlp_engine.process_natural_language(user_id, text, context)
            
            # Merge conversational context with NLP result
            if result.success:
                response = result.response
                response["conversation_context"] = True
                response["conversational_intro"] = conversational_response.get("message", "")
            
            return {
                "success": result.success,
                "response": result.response,
                "intent": result.intent,
                "confidence": result.confidence,
                "processing_time": result.processing_time,
                "fallback_response": result.fallback_response
            }
        
        # Fallback to pure NLP processing
        result = await enhanced_nlp_engine.process_natural_language(user_id, text, context)
        
        return {
            "success": result.success,
            "response": result.response,
            "intent": result.intent,
            "confidence": result.confidence,
            "processing_time": result.processing_time,
            "fallback_response": result.fallback_response
        }
        
    except Exception as e:
        logger.error(f"Error in natural language processing: {e}")
        return {
            "success": False,
            "response": {"type": "error", "message": "I'm having trouble understanding right now. Could you try rephrasing that?"},
            "intent": "error",
            "confidence": 0.0,
            "processing_time": 0.0,
            "fallback_response": "I'm having trouble understanding right now. Could you try rephrasing that?"
        }