# src/intelligent_message_router.py
"""
Intelligent Message Router for Möbius AI Assistant
Fixes the core issues with MCP over-prioritization and improves intent recognition
"""

import asyncio
import logging
import re
import time
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)

class MessageType(Enum):
    """Types of messages"""
    COMMAND = "command"
    GREETING = "greeting"
    QUESTION = "question"
    CASUAL_CHAT = "casual_chat"
    CRYPTO_QUERY = "crypto_query"
    PORTFOLIO_REQUEST = "portfolio_request"
    ALERT_REQUEST = "alert_request"
    HELP_REQUEST = "help_request"
    RESEARCH_REQUEST = "research_request"

class ProcessingStrategy(Enum):
    """Processing strategies"""
    BUILT_IN_COMMAND = "built_in"
    DIRECT_RESPONSE = "direct"
    AI_RESPONSE = "ai"
    MCP_ENHANCED = "mcp_enhanced"
    SILENT_OBSERVE = "silent"

@dataclass
class MessageAnalysis:
    """Analysis result for a message"""
    message_type: MessageType
    processing_strategy: ProcessingStrategy
    confidence: float
    should_respond: bool
    response_reason: str
    extracted_entities: Dict[str, Any]
    urgency_score: float

class IntelligentMessageRouter:
    """
    Intelligent message router that prioritizes built-in commands over MCP
    and properly handles group chat behavior
    """
    
    def __init__(self):
        self.built_in_commands = self._initialize_built_in_commands()
        self.intent_patterns = self._initialize_intent_patterns()
        self.crypto_keywords = self._initialize_crypto_keywords()
        self.casual_patterns = self._initialize_casual_patterns()
        self.group_behavior_rules = self._initialize_group_behavior()
        
    def _initialize_built_in_commands(self) -> Dict[str, Dict[str, Any]]:
        """Initialize built-in command mappings"""
        return {
            # Core commands that should NEVER go to MCP
            "price": {
                "patterns": [
                    r"(?:price|cost|value)\s+(?:of\s+)?(\w+)",
                    r"(\w+)\s+price(?:\s+please)?",
                    r"how much (?:is|does|costs?)\s+(\w+)",
                    r"what'?s\s+(\w+)\s+(?:price|worth|trading)",
                    r"check\s+(\w+)\s+price",
                ],
                "handler": "crypto_price_query",
                "confidence_boost": 0.3
            },
            "portfolio": {
                "patterns": [
                    r"(?:my\s+)?portfolio",
                    r"(?:my\s+)?(?:holdings|balance|assets)",
                    r"show\s+(?:my\s+)?(?:portfolio|holdings|balance)",
                ],
                "handler": "portfolio_command",
                "confidence_boost": 0.4
            },
            "alert": {
                "patterns": [
                    r"(?:set|create|add)\s+(?:an?\s+)?alert",
                    r"alert\s+(?:me\s+)?(?:when|if)",
                    r"notify\s+(?:me\s+)?(?:when|if)",
                ],
                "handler": "alert_command",
                "confidence_boost": 0.4
            },
            "help": {
                "patterns": [
                    r"^(?:help|assistance|support)$",
                    r"what\s+can\s+you\s+do",
                    r"(?:show\s+)?(?:commands|features|capabilities)",
                ],
                "handler": "help_command",
                "confidence_boost": 0.5
            },
            "summary": {
                "patterns": [
                    r"(?:summary|summarize|recap)",
                    r"what\s+(?:happened|did\s+i\s+miss)",
                    r"catch\s+me\s+up",
                ],
                "handler": "summary_command",
                "confidence_boost": 0.4
            },
            "wallet": {
                "patterns": [
                    r"(?:create|new|generate)\s+wallet",
                    r"wallet\s+(?:balance|address)",
                    r"(?:my\s+)?wallet",
                ],
                "handler": "wallet_command",
                "confidence_boost": 0.4
            }
        }
    
    def _initialize_intent_patterns(self) -> Dict[str, List[str]]:
        """Initialize intent recognition patterns"""
        return {
            "greeting": [
                r"^(?:hi|hello|hey|greetings|good\s+(?:morning|afternoon|evening))(?:\s+\w+)?[.!]*$",
                r"^(?:what'?s\s+up|how\s+are\s+you|how'?s\s+it\s+going)(?:\s+\w+)?[.!]*$",
            ],
            "casual_chat": [
                r"^(?:yes|no|ok|okay|sure|thanks|thank\s+you|cool|nice|great|awesome)(?:\s+\w+)*[.!]*$",
                r"^(?:i\s+agree|i\s+disagree|exactly|totally|definitely|absolutely)(?:\s+\w+)*[.!]*$",
                r"^(?:lol|haha|lmao|rofl|😂|🤣)(?:\s+\w+)*[.!]*$",
            ],
            "question": [
                r"^(?:what|who|where|when|why|how)\s+",
                r"\?$",
                r"^(?:is|are|do|does|can|could|would|will)\s+",
            ],
            "crypto_query": [
                r"(?:btc|bitcoin|eth|ethereum|sol|solana|ada|cardano|dot|polkadot)",
                r"(?:defi|yield|farming|staking|liquidity)",
                r"(?:market|trading|exchange|swap)",
            ]
        }
    
    def _initialize_crypto_keywords(self) -> List[str]:
        """Initialize crypto-related keywords"""
        return [
            "btc", "bitcoin", "eth", "ethereum", "sol", "solana", "ada", "cardano",
            "dot", "polkadot", "link", "chainlink", "uni", "uniswap", "aave",
            "matic", "polygon", "avax", "avalanche", "atom", "cosmos", "near",
            "ftm", "fantom", "algo", "algorand", "xrp", "ripple", "ltc", "litecoin",
            "defi", "yield", "farming", "staking", "liquidity", "dex", "cex",
            "market", "trading", "price", "pump", "dump", "moon", "lambo",
            "hodl", "diamond", "hands", "paper", "hands", "ape", "fomo", "fud"
        ]
    
    def _initialize_casual_patterns(self) -> List[str]:
        """Initialize patterns for casual conversation"""
        return [
            r"^(?:yes|no|ok|okay|sure|thanks|thank\s+you|cool|nice|great|awesome)(?:\s+\w+)*[.!]*$",
            r"^(?:i\s+agree|i\s+disagree|exactly|totally|definitely|absolutely)(?:\s+\w+)*[.!]*$",
            r"^(?:lol|haha|lmao|rofl|😂|🤣)(?:\s+\w+)*[.!]*$",
            r"^(?:but|and|so|however|although|though)\s+",
            r"^(?:this|that|it|they|we|i)\s+(?:is|are|was|were|will|would|could|should)\s+",
        ]
    
    def _initialize_group_behavior(self) -> Dict[str, Any]:
        """Initialize group chat behavior rules"""
        return {
            "respond_to_mentions": True,
            "respond_to_replies": True,
            "respond_to_commands": True,
            "respond_to_urgent_crypto": False,  # Disabled by default
            "silent_learning": True,  # Always learn silently
            "context_window": 5,  # Messages to consider for context
            "mention_patterns": [
                r"@mobius",
                r"@möbius", 
                r"mobius",
                r"möbius",
                r"hey\s+bot",
                r"hey\s+ai",
                r"ai\s+assistant",
                r"crypto\s+bot"
            ]
        }
    
    async def analyze_message(
        self, 
        text: str, 
        user_id: int, 
        chat_type: str, 
        is_reply_to_bot: bool = False,
        is_mentioned: bool = False,
        context: Dict[str, Any] = None
    ) -> MessageAnalysis:
        """
        Analyze a message and determine how to process it
        
        Args:
            text: Message text
            user_id: User ID
            chat_type: Type of chat (private, group, supergroup)
            is_reply_to_bot: Whether message is a reply to bot
            is_mentioned: Whether bot is mentioned
            context: Additional context
            
        Returns:
            MessageAnalysis with processing strategy
        """
        
        if not text or not text.strip():
            return MessageAnalysis(
                message_type=MessageType.CASUAL_CHAT,
                processing_strategy=ProcessingStrategy.SILENT_OBSERVE,
                confidence=1.0,
                should_respond=False,
                response_reason="Empty message",
                extracted_entities={},
                urgency_score=0.0
            )
        
        text = text.strip()
        text_lower = text.lower()
        
        # 1. Check if it's a command (highest priority)
        if text.startswith('/'):
            return MessageAnalysis(
                message_type=MessageType.COMMAND,
                processing_strategy=ProcessingStrategy.BUILT_IN_COMMAND,
                confidence=1.0,
                should_respond=True,
                response_reason="Direct command",
                extracted_entities={"command": text.split()[0][1:]},
                urgency_score=0.8
            )
        
        # 2. Check for built-in command patterns (second highest priority)
        built_in_match = self._check_built_in_commands(text_lower)
        if built_in_match:
            command, confidence, entities = built_in_match
            return MessageAnalysis(
                message_type=MessageType.CRYPTO_QUERY if command in ["price", "portfolio", "alert"] else MessageType.QUESTION,
                processing_strategy=ProcessingStrategy.BUILT_IN_COMMAND,
                confidence=confidence,
                should_respond=self._should_respond_in_chat(chat_type, is_mentioned, is_reply_to_bot, True),
                response_reason=f"Built-in command: {command}",
                extracted_entities={"command": command, **entities},
                urgency_score=0.7
            )
        
        # 3. Determine if we should respond in group chats
        if chat_type in ['group', 'supergroup']:
            should_respond = self._should_respond_in_chat(chat_type, is_mentioned, is_reply_to_bot, False)
            if not should_respond:
                return MessageAnalysis(
                    message_type=self._classify_message_type(text_lower),
                    processing_strategy=ProcessingStrategy.SILENT_OBSERVE,
                    confidence=0.8,
                    should_respond=False,
                    response_reason="Silent learning in group",
                    extracted_entities=self._extract_entities(text),
                    urgency_score=0.1
                )
        
        # 4. Classify message type and determine strategy
        message_type = self._classify_message_type(text_lower)
        confidence = self._calculate_confidence(text_lower, message_type)
        
        # 5. Determine processing strategy
        strategy = self._determine_processing_strategy(message_type, confidence, text_lower)
        
        # Determine if we should respond based on chat type and context
        should_respond = self._should_respond_in_chat(chat_type, is_mentioned, is_reply_to_bot, False)
        
        return MessageAnalysis(
            message_type=message_type,
            processing_strategy=strategy,
            confidence=confidence,
            should_respond=should_respond,
            response_reason=f"Classified as {message_type.value}" if should_respond else "Silent learning",
            extracted_entities=self._extract_entities(text),
            urgency_score=self._calculate_urgency(text_lower, message_type)
        )
    
    def _check_built_in_commands(self, text: str) -> Optional[Tuple[str, float, Dict[str, Any]]]:
        """Check if text matches built-in command patterns"""
        
        for command, config in self.built_in_commands.items():
            for pattern in config["patterns"]:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    confidence = 0.8 + config.get("confidence_boost", 0.0)
                    entities = {}
                    
                    # Extract entities from match groups
                    if match.groups():
                        if command == "price":
                            # Smart symbol extraction - prioritize known crypto symbols
                            extracted_symbol = match.group(1).upper()
                            entities["symbol"] = self._extract_crypto_symbol(text, extracted_symbol)
                        elif command == "alert":
                            entities["alert_text"] = text
                    
                    return command, min(confidence, 1.0), entities
        
        return None
    
    def _extract_crypto_symbol(self, text: str, fallback_symbol: str) -> str:
        """Extract crypto symbol intelligently from text"""
        # Known crypto symbols and their aliases
        crypto_symbols = {
            'BTC': ['BITCOIN', 'BTC'],
            'ETH': ['ETHEREUM', 'ETH', 'ETHER'],
            'SOL': ['SOLANA', 'SOL'],
            'ADA': ['CARDANO', 'ADA'],
            'DOT': ['POLKADOT', 'DOT'],
            'LINK': ['CHAINLINK', 'LINK'],
            'UNI': ['UNISWAP', 'UNI'],
            'AAVE': ['AAVE'],
            'MATIC': ['POLYGON', 'MATIC'],
            'AVAX': ['AVALANCHE', 'AVAX'],
            'ATOM': ['COSMOS', 'ATOM'],
            'NEAR': ['NEAR'],
            'FTM': ['FANTOM', 'FTM'],
            'ALGO': ['ALGORAND', 'ALGO'],
            'XRP': ['RIPPLE', 'XRP'],
            'LTC': ['LITECOIN', 'LTC'],
            'DOGE': ['DOGECOIN', 'DOGE'],
            'SHIB': ['SHIBA', 'SHIB', 'SHIBAINU']
        }
        
        text_upper = text.upper()
        
        # First, check if any known crypto symbol appears in the text
        for symbol, aliases in crypto_symbols.items():
            for alias in aliases:
                if alias in text_upper:
                    return symbol
        
        # If no known symbol found, check if fallback is a known symbol
        for symbol, aliases in crypto_symbols.items():
            if fallback_symbol in aliases:
                return symbol
        
        # Return fallback if nothing else matches
        return fallback_symbol
    
    def _should_respond_in_chat(
        self, 
        chat_type: str, 
        is_mentioned: bool, 
        is_reply_to_bot: bool, 
        is_command: bool
    ) -> bool:
        """Determine if bot should respond in this chat"""
        
        # Always respond in private chats
        if chat_type == 'private':
            return True
        
        # In groups, respond only to:
        # 1. Direct mentions
        # 2. Replies to bot
        # 3. Commands
        if chat_type in ['group', 'supergroup']:
            return is_mentioned or is_reply_to_bot or is_command
        
        return False
    
    def _classify_message_type(self, text: str) -> MessageType:
        """Classify the type of message"""
        
        # Check greeting patterns
        for pattern in self.intent_patterns["greeting"]:
            if re.match(pattern, text):
                return MessageType.GREETING
        
        # Check casual chat patterns
        for pattern in self.casual_patterns:
            if re.match(pattern, text):
                return MessageType.CASUAL_CHAT
        
        # Check question patterns
        for pattern in self.intent_patterns["question"]:
            if re.search(pattern, text):
                return MessageType.QUESTION
        
        # Check crypto-related content
        if any(keyword in text for keyword in self.crypto_keywords):
            return MessageType.CRYPTO_QUERY
        
        # Check for specific request types
        if any(word in text for word in ["help", "assistance", "support", "guide"]):
            return MessageType.HELP_REQUEST
        
        if any(word in text for word in ["research", "analyze", "analysis", "study"]):
            return MessageType.RESEARCH_REQUEST
        
        # Default to question if it has question marks or question words
        if "?" in text or any(word in text for word in ["what", "how", "why", "when", "where", "who"]):
            return MessageType.QUESTION
        
        return MessageType.CASUAL_CHAT
    
    def _calculate_confidence(self, text: str, message_type: MessageType) -> float:
        """Calculate confidence score for message classification"""
        
        base_confidence = 0.6
        
        # Boost confidence for clear patterns
        if message_type == MessageType.GREETING:
            if re.match(r"^(?:hi|hello|hey)(?:\s+\w+)?[.!]*$", text):
                base_confidence = 0.9
        
        elif message_type == MessageType.CASUAL_CHAT:
            if re.match(r"^(?:yes|no|ok|okay)(?:\s+\w+)*[.!]*$", text):
                base_confidence = 0.95
        
        elif message_type == MessageType.CRYPTO_QUERY:
            crypto_count = sum(1 for keyword in self.crypto_keywords if keyword in text)
            base_confidence += min(crypto_count * 0.1, 0.3)
        
        elif message_type == MessageType.QUESTION:
            if text.endswith("?"):
                base_confidence += 0.2
            if text.startswith(("what", "how", "why", "when", "where", "who")):
                base_confidence += 0.15
        
        return min(base_confidence, 1.0)
    
    def _determine_processing_strategy(
        self, 
        message_type: MessageType, 
        confidence: float, 
        text: str
    ) -> ProcessingStrategy:
        """Determine the best processing strategy"""
        
        # High confidence built-in responses
        if confidence > 0.8:
            if message_type in [MessageType.GREETING, MessageType.CASUAL_CHAT]:
                return ProcessingStrategy.DIRECT_RESPONSE
            elif message_type in [MessageType.CRYPTO_QUERY, MessageType.PORTFOLIO_REQUEST]:
                return ProcessingStrategy.BUILT_IN_COMMAND
        
        # Medium confidence - use AI but avoid MCP for simple things
        elif confidence > 0.5:
            if message_type == MessageType.CASUAL_CHAT:
                return ProcessingStrategy.DIRECT_RESPONSE
            else:
                return ProcessingStrategy.AI_RESPONSE
        
        # Low confidence - use AI response
        else:
            return ProcessingStrategy.AI_RESPONSE
    
    def _extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract entities from text"""
        entities = {}
        
        # Crypto symbols
        crypto_pattern = r'\b(BTC|ETH|SOL|ADA|DOT|LINK|UNI|AAVE|MATIC|AVAX|ATOM|NEAR|FTM|ALGO|XRP|LTC|BCH|ETC|XLM|VET|THETA|TFUEL|HBAR|ICP|FIL|EOS|TRX|XTZ|DASH|ZEC|QTUM|ONT|ZIL|RVN|DGB|SC|DCR|LSK|ARDR|STRAT|WAVES|NXT|BURST|XEM|MONA|DOGE|SHIB)\b'
        crypto_matches = re.findall(crypto_pattern, text.upper())
        if crypto_matches:
            entities["crypto_symbols"] = crypto_matches
        
        # Price values
        price_pattern = r'\$[\d,]+(?:\.\d{2})?'
        price_matches = re.findall(price_pattern, text)
        if price_matches:
            entities["prices"] = price_matches
        
        # Percentages
        percent_pattern = r'\d+(?:\.\d+)?%'
        percent_matches = re.findall(percent_pattern, text)
        if percent_matches:
            entities["percentages"] = percent_matches
        
        return entities
    
    def _calculate_urgency(self, text: str, message_type: MessageType) -> float:
        """Calculate urgency score"""
        
        urgency = 0.3  # Base urgency
        
        # Urgent keywords
        urgent_keywords = ["urgent", "asap", "quickly", "fast", "now", "immediately", "emergency"]
        if any(keyword in text for keyword in urgent_keywords):
            urgency += 0.4
        
        # Question marks indicate need for response
        if "?" in text:
            urgency += 0.2
        
        # Commands are generally urgent
        if message_type == MessageType.COMMAND:
            urgency += 0.3
        
        # Crypto queries during market hours
        if message_type == MessageType.CRYPTO_QUERY:
            urgency += 0.2
        
        return min(urgency, 1.0)

# Global instance
intelligent_router = IntelligentMessageRouter()

# Export functions for backward compatibility
async def analyze_message_intent(
    text: str, 
    user_id: int, 
    chat_type: str, 
    is_reply_to_bot: bool = False,
    is_mentioned: bool = False,
    context: Dict[str, Any] = None
) -> MessageAnalysis:
    """Analyze message intent using the intelligent router"""
    return await intelligent_router.analyze_message(
        text, user_id, chat_type, is_reply_to_bot, is_mentioned, context
    )

def should_use_mcp(analysis: MessageAnalysis) -> bool:
    """Determine if MCP should be used based on analysis"""
    return analysis.processing_strategy == ProcessingStrategy.MCP_ENHANCED

def should_respond(analysis: MessageAnalysis) -> bool:
    """Determine if bot should respond"""
    return analysis.should_respond

def get_processing_strategy(analysis: MessageAnalysis) -> str:
    """Get the processing strategy as string"""
    return analysis.processing_strategy.value