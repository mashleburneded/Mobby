# src/advanced_conversation_intelligence.py - Enhanced NLP with Deep Conversation Context and Learning
import asyncio
import logging
import time
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import sqlite3
import pickle
from collections import defaultdict, deque
import re

logger = logging.getLogger(__name__)

class IntentCategory(Enum):
    """Categories of user intents"""
    PRICE_QUERY = "price_query"
    PORTFOLIO_MANAGEMENT = "portfolio_management"
    TRADING_SIGNALS = "trading_signals"
    DEFI_RESEARCH = "defi_research"
    WALLET_OPERATIONS = "wallet_operations"
    MARKET_ANALYSIS = "market_analysis"
    NEWS_RESEARCH = "news_research"
    TECHNICAL_ANALYSIS = "technical_analysis"
    GENERAL_CRYPTO = "general_crypto"
    CASUAL_CHAT = "casual_chat"
    HELP_SUPPORT = "help_support"

class ContextType(Enum):
    """Types of conversation context"""
    IMMEDIATE = "immediate"  # Current message context
    SESSION = "session"      # Current session context
    HISTORICAL = "historical" # Long-term user patterns
    MARKET = "market"        # Current market conditions
    TEMPORAL = "temporal"    # Time-based patterns

@dataclass
class ConversationTurn:
    """Single conversation turn"""
    timestamp: datetime
    user_message: str
    bot_response: str
    intent: IntentCategory
    entities: Dict[str, Any]
    confidence: float
    processing_time: float
    user_satisfaction: Optional[float] = None

@dataclass
class EnhancedIntentAnalysis:
    """Comprehensive intent analysis result"""
    primary_intent: IntentCategory
    secondary_intents: List[IntentCategory]
    confidence: float
    entities: Dict[str, Any]
    context_factors: Dict[str, Any]
    conversation_state: str
    recommended_action: str
    learning_feedback: Dict[str, Any]

class PersistentConversationMemory:
    """Persistent storage for conversation context and learning"""
    
    def __init__(self, db_path: str = "data/conversation_memory.db"):
        self.db_path = db_path
        self.connection = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize conversation memory database"""
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS conversation_turns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    timestamp DATETIME NOT NULL,
                    user_message TEXT NOT NULL,
                    bot_response TEXT,
                    intent TEXT NOT NULL,
                    entities TEXT,
                    confidence REAL,
                    processing_time REAL,
                    user_satisfaction REAL,
                    session_id TEXT
                )
            """)
            
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS user_patterns (
                    user_id INTEGER NOT NULL,
                    pattern_type TEXT NOT NULL,
                    pattern_data TEXT NOT NULL,
                    frequency INTEGER DEFAULT 1,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, pattern_type)
                )
            """)
            
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS conversation_context (
                    user_id INTEGER NOT NULL,
                    context_type TEXT NOT NULL,
                    context_data TEXT NOT NULL,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, context_type)
                )
            """)
            
            # Create indexes for performance
            self.connection.execute("CREATE INDEX IF NOT EXISTS idx_turns_user_time ON conversation_turns(user_id, timestamp)")
            self.connection.execute("CREATE INDEX IF NOT EXISTS idx_patterns_user ON user_patterns(user_id)")
            self.connection.execute("CREATE INDEX IF NOT EXISTS idx_context_user ON conversation_context(user_id)")
            
            self.connection.commit()
            logger.info("✅ Conversation memory database initialized")
            
        except Exception as e:
            logger.error(f"Error initializing conversation memory database: {e}")
    
    async def store_conversation_turn(self, user_id: int, turn: ConversationTurn, session_id: str):
        """Store a conversation turn"""
        try:
            self.connection.execute("""
                INSERT INTO conversation_turns 
                (user_id, timestamp, user_message, bot_response, intent, entities, 
                 confidence, processing_time, user_satisfaction, session_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, turn.timestamp, turn.user_message, turn.bot_response,
                turn.intent.value, json.dumps(turn.entities), turn.confidence,
                turn.processing_time, turn.user_satisfaction, session_id
            ))
            self.connection.commit()
        except Exception as e:
            logger.error(f"Error storing conversation turn: {e}")
    
    async def get_rich_context(self, user_id: int, depth: int = 10) -> Dict[str, Any]:
        """Get comprehensive conversation context"""
        try:
            # Get recent conversation turns
            cursor = self.connection.execute("""
                SELECT timestamp, user_message, bot_response, intent, entities, confidence
                FROM conversation_turns 
                WHERE user_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (user_id, depth))
            
            recent_turns = []
            for row in cursor.fetchall():
                recent_turns.append({
                    "timestamp": row[0],
                    "user_message": row[1],
                    "bot_response": row[2],
                    "intent": row[3],
                    "entities": json.loads(row[4]) if row[4] else {},
                    "confidence": row[5]
                })
            
            # Get user patterns
            cursor = self.connection.execute("""
                SELECT pattern_type, pattern_data, frequency
                FROM user_patterns 
                WHERE user_id = ?
            """, (user_id,))
            
            patterns = {}
            for row in cursor.fetchall():
                patterns[row[0]] = {
                    "data": json.loads(row[1]),
                    "frequency": row[2]
                }
            
            # Get stored context
            cursor = self.connection.execute("""
                SELECT context_type, context_data
                FROM conversation_context 
                WHERE user_id = ?
            """, (user_id,))
            
            stored_context = {}
            for row in cursor.fetchall():
                stored_context[row[0]] = json.loads(row[1])
            
            return {
                "recent_turns": recent_turns,
                "user_patterns": patterns,
                "stored_context": stored_context,
                "context_depth": len(recent_turns)
            }
            
        except Exception as e:
            logger.error(f"Error getting rich context: {e}")
            return {"recent_turns": [], "user_patterns": {}, "stored_context": {}}
    
    async def update_user_pattern(self, user_id: int, pattern_type: str, pattern_data: Dict[str, Any]):
        """Update user behavioral patterns"""
        try:
            # Check if pattern exists
            cursor = self.connection.execute("""
                SELECT frequency FROM user_patterns 
                WHERE user_id = ? AND pattern_type = ?
            """, (user_id, pattern_type))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing pattern
                new_frequency = existing[0] + 1
                self.connection.execute("""
                    UPDATE user_patterns 
                    SET pattern_data = ?, frequency = ?, last_updated = CURRENT_TIMESTAMP
                    WHERE user_id = ? AND pattern_type = ?
                """, (json.dumps(pattern_data), new_frequency, user_id, pattern_type))
            else:
                # Insert new pattern
                self.connection.execute("""
                    INSERT INTO user_patterns (user_id, pattern_type, pattern_data)
                    VALUES (?, ?, ?)
                """, (user_id, pattern_type, json.dumps(pattern_data)))
            
            self.connection.commit()
            
        except Exception as e:
            logger.error(f"Error updating user pattern: {e}")

class MultiLayerIntentClassifier:
    """Advanced multi-layer intent classification with learning"""
    
    def __init__(self):
        self.intent_patterns = self._initialize_intent_patterns()
        self.entity_extractors = self._initialize_entity_extractors()
        self.confidence_thresholds = {
            IntentCategory.PRICE_QUERY: 0.8,
            IntentCategory.PORTFOLIO_MANAGEMENT: 0.7,
            IntentCategory.TRADING_SIGNALS: 0.75,
            IntentCategory.DEFI_RESEARCH: 0.7,
            IntentCategory.WALLET_OPERATIONS: 0.8,
            IntentCategory.MARKET_ANALYSIS: 0.7,
            IntentCategory.NEWS_RESEARCH: 0.7,
            IntentCategory.TECHNICAL_ANALYSIS: 0.75,
            IntentCategory.GENERAL_CRYPTO: 0.6,
            IntentCategory.CASUAL_CHAT: 0.5,
            IntentCategory.HELP_SUPPORT: 0.8
        }
    
    def _initialize_intent_patterns(self) -> Dict[IntentCategory, List[str]]:
        """Initialize intent recognition patterns"""
        return {
            IntentCategory.PRICE_QUERY: [
                r"(?:price|cost|value|worth)\s+(?:of\s+)?(\w+)",
                r"(\w+)\s+price",
                r"how much is (\w+)",
                r"(\w+)\s+\$",
                r"current\s+(\w+)",
                r"(\w+)\s+quote"
            ],
            IntentCategory.PORTFOLIO_MANAGEMENT: [
                r"(?:my\s+)?portfolio",
                r"holdings?",
                r"balance",
                r"assets?",
                r"investments?",
                r"rebalance",
                r"allocation"
            ],
            IntentCategory.TRADING_SIGNALS: [
                r"trading\s+signals?",
                r"buy\s+sell",
                r"trade\s+recommendations?",
                r"when\s+to\s+(?:buy|sell)",
                r"entry\s+points?",
                r"exit\s+strategy"
            ],
            IntentCategory.DEFI_RESEARCH: [
                r"defi",
                r"yield\s+farming",
                r"liquidity\s+pool",
                r"staking",
                r"apy",
                r"protocol",
                r"tvl"
            ],
            IntentCategory.WALLET_OPERATIONS: [
                r"wallet",
                r"address",
                r"transaction",
                r"transfer",
                r"send",
                r"receive",
                r"0x[a-fA-F0-9]+"
            ],
            IntentCategory.MARKET_ANALYSIS: [
                r"market\s+(?:analysis|overview|sentiment)",
                r"market\s+cap",
                r"volume",
                r"trends?",
                r"bullish|bearish",
                r"market\s+condition"
            ],
            IntentCategory.NEWS_RESEARCH: [
                r"news",
                r"updates?",
                r"announcement",
                r"events?",
                r"sentiment",
                r"social"
            ],
            IntentCategory.TECHNICAL_ANALYSIS: [
                r"technical\s+analysis",
                r"chart",
                r"indicators?",
                r"rsi",
                r"macd",
                r"support|resistance",
                r"fibonacci"
            ],
            IntentCategory.GENERAL_CRYPTO: [
                r"crypto",
                r"bitcoin",
                r"ethereum",
                r"blockchain",
                r"altcoin",
                r"cryptocurrency"
            ],
            IntentCategory.CASUAL_CHAT: [
                r"hello|hi|hey",
                r"how are you",
                r"thanks?|thank you",
                r"good|great|awesome",
                r"ok|okay",
                r"bye|goodbye"
            ],
            IntentCategory.HELP_SUPPORT: [
                r"help",
                r"how\s+(?:do|can)",
                r"what\s+(?:is|are)",
                r"explain",
                r"tutorial",
                r"guide",
                r"support"
            ]
        }
    
    def _initialize_entity_extractors(self) -> Dict[str, str]:
        """Initialize entity extraction patterns"""
        return {
            "cryptocurrency": r"\b(?:BTC|ETH|SOL|ADA|DOT|AVAX|MATIC|LINK|UNI|AAVE|COMP|MKR|SNX|CRV|YFI|SUSHI|1INCH)\b",
            "price": r"\$?(\d+(?:,\d{3})*(?:\.\d{2})?)",
            "percentage": r"(\d+(?:\.\d+)?)\s*%",
            "wallet_address": r"(0x[a-fA-F0-9]{40})",
            "timeframe": r"\b(?:1h|4h|1d|1w|1m|daily|weekly|monthly|hourly)\b",
            "amount": r"(\d+(?:\.\d+)?)\s*(\w+)"
        }
    
    async def classify_with_learning(self, message: str, conversation_context: Dict[str, Any],
                                   user_preferences: Dict[str, Any], market_context: Dict[str, Any],
                                   temporal_context: Dict[str, Any]) -> EnhancedIntentAnalysis:
        """Classify intent with comprehensive context and learning"""
        
        # Layer 1: Pattern-based classification
        pattern_scores = await self._pattern_based_classification(message)
        
        # Layer 2: Context-aware adjustment
        context_adjusted_scores = await self._context_aware_adjustment(
            pattern_scores, conversation_context, user_preferences
        )
        
        # Layer 3: Market and temporal context
        final_scores = await self._market_temporal_adjustment(
            context_adjusted_scores, market_context, temporal_context
        )
        
        # Layer 4: Learning-based refinement
        refined_scores = await self._learning_based_refinement(
            final_scores, conversation_context.get("user_patterns", {})
        )
        
        # Determine primary and secondary intents
        sorted_intents = sorted(refined_scores.items(), key=lambda x: x[1], reverse=True)
        primary_intent = sorted_intents[0][0]
        primary_confidence = sorted_intents[0][1]
        
        secondary_intents = [
            intent for intent, score in sorted_intents[1:4] 
            if score > 0.3  # Threshold for secondary intents
        ]
        
        # Extract entities
        entities = await self._extract_entities(message, primary_intent)
        
        # Determine conversation state and recommended action
        conversation_state = await self._determine_conversation_state(
            conversation_context, primary_intent
        )
        
        recommended_action = await self._recommend_action(
            primary_intent, entities, conversation_state
        )
        
        # Generate learning feedback
        learning_feedback = await self._generate_learning_feedback(
            message, primary_intent, primary_confidence, conversation_context
        )
        
        return EnhancedIntentAnalysis(
            primary_intent=primary_intent,
            secondary_intents=secondary_intents,
            confidence=primary_confidence,
            entities=entities,
            context_factors={
                "conversation_depth": len(conversation_context.get("recent_turns", [])),
                "user_patterns": len(conversation_context.get("user_patterns", {})),
                "market_conditions": market_context,
                "temporal_factors": temporal_context
            },
            conversation_state=conversation_state,
            recommended_action=recommended_action,
            learning_feedback=learning_feedback
        )
    
    async def _pattern_based_classification(self, message: str) -> Dict[IntentCategory, float]:
        """Basic pattern-based intent classification"""
        scores = {intent: 0.0 for intent in IntentCategory}
        message_lower = message.lower()
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    # Weight by pattern specificity
                    specificity = len(pattern) / 100.0
                    scores[intent] += min(0.3 + specificity, 0.8)
        
        # Normalize scores
        max_score = max(scores.values()) if any(scores.values()) else 1.0
        return {intent: score / max_score for intent, score in scores.items()}
    
    async def _context_aware_adjustment(self, pattern_scores: Dict[IntentCategory, float],
                                      conversation_context: Dict[str, Any],
                                      user_preferences: Dict[str, Any]) -> Dict[IntentCategory, float]:
        """Adjust scores based on conversation context"""
        adjusted_scores = pattern_scores.copy()
        
        # Recent conversation context
        recent_turns = conversation_context.get("recent_turns", [])
        if recent_turns:
            # Boost related intents from recent conversation
            recent_intents = [turn.get("intent") for turn in recent_turns[-3:]]
            for intent_str in recent_intents:
                try:
                    intent = IntentCategory(intent_str)
                    adjusted_scores[intent] *= 1.2  # 20% boost for recent context
                except ValueError:
                    continue
        
        # User preferences
        preferred_topics = user_preferences.get("preferred_topics", [])
        for topic in preferred_topics:
            try:
                intent = IntentCategory(topic)
                adjusted_scores[intent] *= 1.1  # 10% boost for preferences
            except ValueError:
                continue
        
        return adjusted_scores
    
    async def _market_temporal_adjustment(self, scores: Dict[IntentCategory, float],
                                        market_context: Dict[str, Any],
                                        temporal_context: Dict[str, Any]) -> Dict[IntentCategory, float]:
        """Adjust scores based on market and temporal context"""
        adjusted_scores = scores.copy()
        
        # Market volatility affects certain intents
        volatility = market_context.get("volatility", "normal")
        if volatility == "high":
            # Boost trading and analysis intents during high volatility
            adjusted_scores[IntentCategory.TRADING_SIGNALS] *= 1.3
            adjusted_scores[IntentCategory.MARKET_ANALYSIS] *= 1.2
            adjusted_scores[IntentCategory.TECHNICAL_ANALYSIS] *= 1.2
        
        # Time of day affects intent likelihood
        hour = temporal_context.get("hour", 12)
        if 9 <= hour <= 16:  # Market hours
            # Boost trading-related intents during market hours
            adjusted_scores[IntentCategory.TRADING_SIGNALS] *= 1.1
            adjusted_scores[IntentCategory.MARKET_ANALYSIS] *= 1.1
        elif 22 <= hour or hour <= 6:  # Night hours
            # Boost research and casual intents at night
            adjusted_scores[IntentCategory.NEWS_RESEARCH] *= 1.1
            adjusted_scores[IntentCategory.CASUAL_CHAT] *= 1.2
        
        return adjusted_scores
    
    async def _learning_based_refinement(self, scores: Dict[IntentCategory, float],
                                       user_patterns: Dict[str, Any]) -> Dict[IntentCategory, float]:
        """Refine scores based on learned user patterns"""
        refined_scores = scores.copy()
        
        # Apply learned intent preferences
        intent_preferences = user_patterns.get("intent_preferences", {})
        for intent_str, preference_score in intent_preferences.get("data", {}).items():
            try:
                intent = IntentCategory(intent_str)
                # Apply preference with diminishing returns
                preference_multiplier = 1.0 + (preference_score * 0.1)
                refined_scores[intent] *= preference_multiplier
            except ValueError:
                continue
        
        # Apply temporal patterns
        temporal_patterns = user_patterns.get("temporal_patterns", {})
        current_hour = datetime.now().hour
        hour_patterns = temporal_patterns.get("data", {}).get(str(current_hour), {})
        for intent_str, frequency in hour_patterns.items():
            try:
                intent = IntentCategory(intent_str)
                # Boost based on historical frequency at this hour
                frequency_multiplier = 1.0 + (frequency * 0.05)
                refined_scores[intent] *= frequency_multiplier
            except ValueError:
                continue
        
        return refined_scores
    
    async def _extract_entities(self, message: str, primary_intent: IntentCategory) -> Dict[str, Any]:
        """Extract entities relevant to the primary intent"""
        entities = {}
        
        for entity_type, pattern in self.entity_extractors.items():
            matches = re.findall(pattern, message, re.IGNORECASE)
            if matches:
                entities[entity_type] = matches
        
        # Intent-specific entity extraction
        if primary_intent == IntentCategory.PRICE_QUERY:
            # Extract specific cryptocurrency mentions
            crypto_mentions = re.findall(r'\b(?:BTC|ETH|SOL|ADA|DOT|AVAX|MATIC|LINK)\b', message, re.IGNORECASE)
            if crypto_mentions:
                entities["target_crypto"] = crypto_mentions[0].upper()
        
        elif primary_intent == IntentCategory.TRADING_SIGNALS:
            # Extract trading-related entities
            action_words = re.findall(r'\b(?:buy|sell|hold|long|short)\b', message, re.IGNORECASE)
            if action_words:
                entities["trading_action"] = action_words[0].lower()
        
        return entities
    
    async def _determine_conversation_state(self, conversation_context: Dict[str, Any],
                                          primary_intent: IntentCategory) -> str:
        """Determine the current conversation state"""
        recent_turns = conversation_context.get("recent_turns", [])
        
        if not recent_turns:
            return "new_conversation"
        
        # Check for continuation patterns
        recent_intents = [turn.get("intent") for turn in recent_turns[-3:]]
        
        if len(set(recent_intents)) == 1:
            return "focused_discussion"
        elif len(recent_turns) > 5:
            return "extended_conversation"
        elif primary_intent.value in recent_intents:
            return "topic_continuation"
        else:
            return "topic_switch"
    
    async def _recommend_action(self, primary_intent: IntentCategory,
                              entities: Dict[str, Any], conversation_state: str) -> str:
        """Recommend the best action based on intent and context"""
        
        if primary_intent in [IntentCategory.PRICE_QUERY, IntentCategory.MARKET_ANALYSIS]:
            return "fetch_market_data"
        elif primary_intent == IntentCategory.PORTFOLIO_MANAGEMENT:
            return "analyze_portfolio"
        elif primary_intent == IntentCategory.TRADING_SIGNALS:
            return "generate_trading_signals"
        elif primary_intent == IntentCategory.DEFI_RESEARCH:
            return "research_defi_protocols"
        elif primary_intent == IntentCategory.WALLET_OPERATIONS:
            return "process_wallet_request"
        elif primary_intent == IntentCategory.NEWS_RESEARCH:
            return "fetch_crypto_news"
        elif primary_intent == IntentCategory.TECHNICAL_ANALYSIS:
            return "perform_technical_analysis"
        elif primary_intent == IntentCategory.HELP_SUPPORT:
            return "provide_help"
        elif primary_intent == IntentCategory.CASUAL_CHAT:
            return "casual_response"
        else:
            return "general_crypto_response"
    
    async def _generate_learning_feedback(self, message: str, primary_intent: IntentCategory,
                                        confidence: float, conversation_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate feedback for continuous learning"""
        return {
            "confidence_level": "high" if confidence > 0.8 else "medium" if confidence > 0.6 else "low",
            "pattern_matches": len([p for patterns in self.intent_patterns[primary_intent] 
                                  for p in patterns if re.search(p, message.lower())]),
            "context_influence": len(conversation_context.get("recent_turns", [])) > 0,
            "suggested_improvements": {
                "add_patterns": confidence < 0.7,
                "refine_context": len(conversation_context.get("recent_turns", [])) < 3,
                "update_thresholds": confidence < 0.5
            }
        }

class ConversationContextAnalyzer:
    """Analyze conversation context for better understanding"""
    
    def __init__(self):
        self.context_weights = {
            ContextType.IMMEDIATE: 0.4,
            ContextType.SESSION: 0.3,
            ContextType.HISTORICAL: 0.2,
            ContextType.MARKET: 0.05,
            ContextType.TEMPORAL: 0.05
        }
    
    async def analyze_context(self, user_id: int, current_message: str,
                            conversation_memory: PersistentConversationMemory) -> Dict[str, Any]:
        """Analyze comprehensive conversation context"""
        
        # Get rich context from memory
        rich_context = await conversation_memory.get_rich_context(user_id, depth=20)
        
        # Analyze immediate context
        immediate_context = await self._analyze_immediate_context(current_message)
        
        # Analyze session context
        session_context = await self._analyze_session_context(rich_context["recent_turns"])
        
        # Analyze historical patterns
        historical_context = await self._analyze_historical_context(rich_context["user_patterns"])
        
        # Get market context
        market_context = await self._get_market_context()
        
        # Get temporal context
        temporal_context = await self._get_temporal_context()
        
        return {
            ContextType.IMMEDIATE.value: immediate_context,
            ContextType.SESSION.value: session_context,
            ContextType.HISTORICAL.value: historical_context,
            ContextType.MARKET.value: market_context,
            ContextType.TEMPORAL.value: temporal_context,
            "context_summary": await self._generate_context_summary(
                immediate_context, session_context, historical_context
            )
        }
    
    async def _analyze_immediate_context(self, message: str) -> Dict[str, Any]:
        """Analyze immediate message context"""
        return {
            "message_length": len(message),
            "word_count": len(message.split()),
            "question_words": len(re.findall(r'\b(?:what|how|when|where|why|which|who)\b', message, re.IGNORECASE)),
            "urgency_indicators": len(re.findall(r'\b(?:urgent|asap|quickly|now|immediately)\b', message, re.IGNORECASE)),
            "sentiment_indicators": {
                "positive": len(re.findall(r'\b(?:good|great|awesome|excellent|amazing)\b', message, re.IGNORECASE)),
                "negative": len(re.findall(r'\b(?:bad|terrible|awful|horrible|disappointed)\b', message, re.IGNORECASE)),
                "neutral": len(re.findall(r'\b(?:okay|fine|normal|average)\b', message, re.IGNORECASE))
            }
        }
    
    async def _analyze_session_context(self, recent_turns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze current session context"""
        if not recent_turns:
            return {"session_length": 0, "topic_consistency": 0, "engagement_level": 0}
        
        # Calculate session metrics
        session_length = len(recent_turns)
        
        # Topic consistency
        intents = [turn.get("intent") for turn in recent_turns]
        unique_intents = len(set(intents))
        topic_consistency = 1.0 - (unique_intents / max(session_length, 1))
        
        # Engagement level based on response times and message lengths
        avg_confidence = sum(turn.get("confidence", 0) for turn in recent_turns) / session_length
        
        return {
            "session_length": session_length,
            "topic_consistency": topic_consistency,
            "engagement_level": avg_confidence,
            "dominant_intent": max(set(intents), key=intents.count) if intents else None,
            "intent_distribution": {intent: intents.count(intent) for intent in set(intents)}
        }
    
    async def _analyze_historical_context(self, user_patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze historical user patterns"""
        if not user_patterns:
            return {"pattern_count": 0, "established_preferences": False}
        
        return {
            "pattern_count": len(user_patterns),
            "established_preferences": len(user_patterns) > 5,
            "most_frequent_patterns": sorted(
                user_patterns.items(), 
                key=lambda x: x[1].get("frequency", 0), 
                reverse=True
            )[:3],
            "pattern_diversity": len(user_patterns)
        }
    
    async def _get_market_context(self) -> Dict[str, Any]:
        """Get current market context"""
        # Mock market context (replace with real market data)
        return {
            "volatility": "normal",
            "trend": "bullish",
            "major_events": [],
            "market_hours": 9 <= datetime.now().hour <= 16
        }
    
    async def _get_temporal_context(self) -> Dict[str, Any]:
        """Get temporal context"""
        now = datetime.now()
        return {
            "hour": now.hour,
            "day_of_week": now.weekday(),
            "is_weekend": now.weekday() >= 5,
            "is_market_hours": 9 <= now.hour <= 16,
            "time_zone": "UTC"
        }
    
    async def _generate_context_summary(self, immediate: Dict[str, Any],
                                      session: Dict[str, Any],
                                      historical: Dict[str, Any]) -> str:
        """Generate a human-readable context summary"""
        summary_parts = []
        
        # Immediate context
        if immediate["urgency_indicators"] > 0:
            summary_parts.append("urgent request")
        
        # Session context
        if session["session_length"] > 5:
            summary_parts.append("extended conversation")
        if session["topic_consistency"] > 0.7:
            summary_parts.append("focused discussion")
        
        # Historical context
        if historical["established_preferences"]:
            summary_parts.append("returning user with preferences")
        
        return ", ".join(summary_parts) if summary_parts else "standard interaction"

class AdaptiveLearningEngine:
    """Continuous learning engine for improving conversation intelligence"""
    
    def __init__(self, conversation_memory: PersistentConversationMemory):
        self.conversation_memory = conversation_memory
        self.learning_rate = 0.1
        self.feedback_buffer = deque(maxlen=1000)
    
    async def learn_from_interaction(self, message: str, analysis_result: EnhancedIntentAnalysis):
        """Learn from each interaction to improve future performance"""
        
        # Extract learning signals
        learning_signals = {
            "intent_confidence": analysis_result.confidence,
            "entity_extraction_success": len(analysis_result.entities) > 0,
            "context_utilization": len(analysis_result.context_factors) > 0,
            "recommended_action": analysis_result.recommended_action
        }
        
        # Store in feedback buffer
        self.feedback_buffer.append({
            "timestamp": datetime.now(),
            "message": message,
            "analysis": asdict(analysis_result),
            "learning_signals": learning_signals
        })
        
        # Periodic learning updates
        if len(self.feedback_buffer) % 100 == 0:
            await self._update_learning_models()
    
    async def _update_learning_models(self):
        """Update learning models based on accumulated feedback"""
        logger.info("Updating learning models based on recent interactions")
        
        # Analyze recent feedback for patterns
        recent_feedback = list(self.feedback_buffer)[-100:]
        
        # Calculate success metrics
        avg_confidence = sum(f["learning_signals"]["intent_confidence"] for f in recent_feedback) / len(recent_feedback)
        entity_success_rate = sum(f["learning_signals"]["entity_extraction_success"] for f in recent_feedback) / len(recent_feedback)
        
        logger.info(f"Learning metrics - Avg confidence: {avg_confidence:.2f}, Entity success: {entity_success_rate:.2f}")
        
        # Update pattern weights based on success rates
        # This would involve more sophisticated ML in a production system

class AdvancedConversationIntelligence:
    """Main class orchestrating advanced conversation intelligence"""
    
    def __init__(self):
        self.conversation_memory = PersistentConversationMemory()
        self.intent_classifier = MultiLayerIntentClassifier()
        self.context_analyzer = ConversationContextAnalyzer()
        self.learning_engine = AdaptiveLearningEngine(self.conversation_memory)
        self.session_manager = {}  # Track active sessions
    
    async def analyze_with_full_context(self, message: str, user_id: int) -> EnhancedIntentAnalysis:
        """Analyze message with comprehensive context and learning"""
        
        # Get or create session
        session_id = self._get_or_create_session(user_id)
        
        # Analyze conversation context
        context = await self.context_analyzer.analyze_context(
            user_id, message, self.conversation_memory
        )
        
        # Get user preferences (mock for now)
        user_preferences = await self._get_user_preferences(user_id)
        
        # Perform multi-layer intent classification
        analysis_result = await self.intent_classifier.classify_with_learning(
            message=message,
            conversation_context=context,
            user_preferences=user_preferences,
            market_context=context[ContextType.MARKET.value],
            temporal_context=context[ContextType.TEMPORAL.value]
        )
        
        # Learn from this interaction
        await self.learning_engine.learn_from_interaction(message, analysis_result)
        
        # Store conversation turn
        turn = ConversationTurn(
            timestamp=datetime.now(),
            user_message=message,
            bot_response="",  # Will be filled later
            intent=analysis_result.primary_intent,
            entities=analysis_result.entities,
            confidence=analysis_result.confidence,
            processing_time=0.0  # Will be calculated
        )
        
        await self.conversation_memory.store_conversation_turn(user_id, turn, session_id)
        
        # Update user patterns
        await self._update_user_patterns(user_id, analysis_result)
        
        return analysis_result
    
    def _get_or_create_session(self, user_id: int) -> str:
        """Get or create a session for the user"""
        current_time = datetime.now()
        
        # Check if user has an active session (within last 30 minutes)
        if user_id in self.session_manager:
            last_activity = self.session_manager[user_id]["last_activity"]
            if current_time - last_activity < timedelta(minutes=30):
                self.session_manager[user_id]["last_activity"] = current_time
                return self.session_manager[user_id]["session_id"]
        
        # Create new session
        session_id = f"session_{user_id}_{int(current_time.timestamp())}"
        self.session_manager[user_id] = {
            "session_id": session_id,
            "start_time": current_time,
            "last_activity": current_time
        }
        
        return session_id
    
    async def _get_user_preferences(self, user_id: int) -> Dict[str, Any]:
        """Get user preferences (mock implementation)"""
        # In a real implementation, this would fetch from user settings
        return {
            "preferred_topics": ["price_query", "market_analysis"],
            "notification_preferences": {"price_alerts": True},
            "interaction_style": "detailed"
        }
    
    async def _update_user_patterns(self, user_id: int, analysis_result: EnhancedIntentAnalysis):
        """Update user behavioral patterns"""
        
        # Update intent preferences
        intent_pattern = {
            "intent": analysis_result.primary_intent.value,
            "confidence": analysis_result.confidence,
            "timestamp": datetime.now().isoformat()
        }
        
        await self.conversation_memory.update_user_pattern(
            user_id, "intent_preferences", intent_pattern
        )
        
        # Update temporal patterns
        current_hour = datetime.now().hour
        temporal_pattern = {
            str(current_hour): {
                analysis_result.primary_intent.value: 1
            }
        }
        
        await self.conversation_memory.update_user_pattern(
            user_id, "temporal_patterns", temporal_pattern
        )

# Global instance
advanced_conversation_intelligence = AdvancedConversationIntelligence()

# Convenience functions
async def analyze_message_with_intelligence(message: str, user_id: int) -> EnhancedIntentAnalysis:
    """Analyze message with advanced conversation intelligence"""
    return await advanced_conversation_intelligence.analyze_with_full_context(message, user_id)

async def get_conversation_insights(user_id: int) -> Dict[str, Any]:
    """Get conversation insights for a user"""
    context = await advanced_conversation_intelligence.context_analyzer.analyze_context(
        user_id, "", advanced_conversation_intelligence.conversation_memory
    )
    return context