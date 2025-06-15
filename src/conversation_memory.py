# src/conversation_memory.py
"""
Advanced Conversation Memory System
Maintains context, learns user preferences, and provides intelligent conversation flow
"""

import asyncio
import logging
import json
import sqlite3
import hashlib
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import deque, defaultdict
from enum import Enum
import threading

logger = logging.getLogger(__name__)

class MemoryType(Enum):
    """Types of memory storage"""
    SHORT_TERM = "short_term"      # Last 5 messages
    MEDIUM_TERM = "medium_term"    # Session context
    LONG_TERM = "long_term"        # User preferences and patterns
    SEMANTIC = "semantic"          # Topic and entity relationships

class UserExperienceLevel(Enum):
    """User experience levels for response adaptation"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

@dataclass
class ConversationMessage:
    """Individual conversation message"""
    message_id: str
    user_id: int
    timestamp: datetime
    text: str
    intent: Optional[str]
    entities: List[Dict]
    sentiment: Dict
    response_text: Optional[str]
    response_time: float
    success: bool
    feedback_score: Optional[float]

@dataclass
class UserProfile:
    """Comprehensive user profile"""
    user_id: int
    username: str
    experience_level: UserExperienceLevel
    preferred_topics: List[str]
    favorite_cryptocurrencies: List[str]
    trading_style: Optional[str]  # "conservative", "moderate", "aggressive"
    risk_tolerance: Optional[str]  # "low", "medium", "high"
    preferred_response_style: str  # "detailed", "concise", "technical"
    timezone: Optional[str]
    language: str
    interaction_count: int
    first_interaction: datetime
    last_interaction: datetime
    satisfaction_score: float
    common_questions: List[str]
    avoided_topics: List[str]

@dataclass
class TopicContext:
    """Context for specific topics"""
    topic: str
    mentioned_entities: Dict[str, int]  # entity -> mention count
    last_mentioned: datetime
    user_interest_score: float
    related_topics: List[str]
    common_questions: List[str]

@dataclass
class SessionContext:
    """Current session context"""
    session_id: str
    user_id: int
    start_time: datetime
    last_activity: datetime
    current_topic: Optional[str]
    topic_history: List[str]
    mentioned_entities: Dict[str, Any]
    conversation_flow: List[str]  # sequence of intents
    user_mood: str  # derived from sentiment analysis
    session_goals: List[str]  # inferred user goals
    unresolved_questions: List[str]

class ConversationMemorySystem:
    """Advanced conversation memory system with multi-level storage"""
    
    def __init__(self, db_path: str = "data/conversation_memory.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self.short_term_memory = defaultdict(lambda: deque(maxlen=5))  # user_id -> messages
        self.session_contexts = {}  # session_id -> SessionContext
        self.user_profiles = {}  # user_id -> UserProfile
        self.topic_contexts = defaultdict(dict)  # user_id -> {topic -> TopicContext}
        self._initialize_database()
        self._load_user_profiles()
    
    def _initialize_database(self):
        """Initialize SQLite database for persistent memory"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversation_messages (
                    message_id TEXT PRIMARY KEY,
                    user_id INTEGER,
                    timestamp TEXT,
                    text TEXT,
                    intent TEXT,
                    entities TEXT,
                    sentiment TEXT,
                    response_text TEXT,
                    response_time REAL,
                    success BOOLEAN,
                    feedback_score REAL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    experience_level TEXT,
                    preferred_topics TEXT,
                    favorite_cryptocurrencies TEXT,
                    trading_style TEXT,
                    risk_tolerance TEXT,
                    preferred_response_style TEXT,
                    timezone TEXT,
                    language TEXT,
                    interaction_count INTEGER,
                    first_interaction TEXT,
                    last_interaction TEXT,
                    satisfaction_score REAL,
                    common_questions TEXT,
                    avoided_topics TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS topic_contexts (
                    user_id INTEGER,
                    topic TEXT,
                    mentioned_entities TEXT,
                    last_mentioned TEXT,
                    user_interest_score REAL,
                    related_topics TEXT,
                    common_questions TEXT,
                    PRIMARY KEY (user_id, topic)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS session_contexts (
                    session_id TEXT PRIMARY KEY,
                    user_id INTEGER,
                    start_time TEXT,
                    last_activity TEXT,
                    current_topic TEXT,
                    topic_history TEXT,
                    mentioned_entities TEXT,
                    conversation_flow TEXT,
                    user_mood TEXT,
                    session_goals TEXT,
                    unresolved_questions TEXT
                )
            """)
            
            # Create indexes for better performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_user_id ON conversation_messages(user_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON conversation_messages(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_topic_contexts_user_id ON topic_contexts(user_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_session_contexts_user_id ON session_contexts(user_id)")
    
    def _load_user_profiles(self):
        """Load user profiles from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT * FROM user_profiles")
                for row in cursor.fetchall():
                    user_id = row[0]
                    self.user_profiles[user_id] = UserProfile(
                        user_id=row[0],
                        username=row[1],
                        experience_level=UserExperienceLevel(row[2]) if row[2] else UserExperienceLevel.BEGINNER,
                        preferred_topics=json.loads(row[3]) if row[3] else [],
                        favorite_cryptocurrencies=json.loads(row[4]) if row[4] else [],
                        trading_style=row[5],
                        risk_tolerance=row[6],
                        preferred_response_style=row[7] or "detailed",
                        timezone=row[8],
                        language=row[9] or "en",
                        interaction_count=row[10] or 0,
                        first_interaction=datetime.fromisoformat(row[11]) if row[11] else datetime.now(),
                        last_interaction=datetime.fromisoformat(row[12]) if row[12] else datetime.now(),
                        satisfaction_score=row[13] or 0.0,
                        common_questions=json.loads(row[14]) if row[14] else [],
                        avoided_topics=json.loads(row[15]) if row[15] else []
                    )
        except Exception as e:
            logger.error(f"Error loading user profiles: {e}")
    
    async def store_message(self, message: ConversationMessage):
        """Store a conversation message in memory and database"""
        with self.lock:
            # Store in short-term memory
            self.short_term_memory[message.user_id].append(message)
            
            # Store in database
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("""
                        INSERT OR REPLACE INTO conversation_messages 
                        (message_id, user_id, timestamp, text, intent, entities, sentiment, 
                         response_text, response_time, success, feedback_score)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        message.message_id,
                        message.user_id,
                        message.timestamp.isoformat(),
                        message.text,
                        message.intent,
                        json.dumps(message.entities),
                        json.dumps(message.sentiment),
                        message.response_text,
                        message.response_time,
                        message.success,
                        message.feedback_score
                    ))
            except Exception as e:
                logger.error(f"Error storing message in database: {e}")
            
            # Update user profile
            await self._update_user_profile(message)
            
            # Update topic contexts
            await self._update_topic_contexts(message)
    
    async def get_conversation_context(self, user_id: int, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive conversation context for a user"""
        context = {
            "short_term_messages": list(self.short_term_memory[user_id]),
            "user_profile": self.user_profiles.get(user_id),
            "topic_contexts": self.topic_contexts.get(user_id, {}),
            "session_context": None,
            "conversation_patterns": await self._analyze_conversation_patterns(user_id),
            "recommended_topics": await self._get_recommended_topics(user_id),
            "personalization_hints": await self._get_personalization_hints(user_id)
        }
        
        if session_id and session_id in self.session_contexts:
            context["session_context"] = self.session_contexts[session_id]
        
        return context
    
    async def start_session(self, user_id: int, session_id: str) -> SessionContext:
        """Start a new conversation session"""
        session_context = SessionContext(
            session_id=session_id,
            user_id=user_id,
            start_time=datetime.now(),
            last_activity=datetime.now(),
            current_topic=None,
            topic_history=[],
            mentioned_entities={},
            conversation_flow=[],
            user_mood="neutral",
            session_goals=[],
            unresolved_questions=[]
        )
        
        self.session_contexts[session_id] = session_context
        return session_context
    
    async def update_session(self, session_id: str, intent: str, entities: List[Dict], sentiment: Dict):
        """Update session context with new interaction"""
        if session_id not in self.session_contexts:
            return
        
        session = self.session_contexts[session_id]
        session.last_activity = datetime.now()
        session.conversation_flow.append(intent)
        
        # Update mentioned entities
        for entity in entities:
            entity_key = f"{entity.get('type')}:{entity.get('value')}"
            session.mentioned_entities[entity_key] = session.mentioned_entities.get(entity_key, 0) + 1
        
        # Update user mood based on sentiment
        compound_score = sentiment.get('compound_score', 0)
        if compound_score > 0.3:
            session.user_mood = "positive"
        elif compound_score < -0.3:
            session.user_mood = "negative"
        else:
            session.user_mood = "neutral"
        
        # Infer session goals
        await self._infer_session_goals(session, intent, entities)
        
        # Store session in database
        await self._store_session_context(session)
    
    async def get_user_profile(self, user_id: int) -> UserProfile:
        """Get or create user profile"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserProfile(
                user_id=user_id,
                username=f"user_{user_id}",
                experience_level=UserExperienceLevel.BEGINNER,
                preferred_topics=[],
                favorite_cryptocurrencies=[],
                trading_style=None,
                risk_tolerance=None,
                preferred_response_style="detailed",
                timezone=None,
                language="en",
                interaction_count=0,
                first_interaction=datetime.now(),
                last_interaction=datetime.now(),
                satisfaction_score=0.0,
                common_questions=[],
                avoided_topics=[]
            )
            await self._save_user_profile(self.user_profiles[user_id])
        
        return self.user_profiles[user_id]
    
    async def update_user_preferences(self, user_id: int, preferences: Dict[str, Any]):
        """Update user preferences"""
        profile = await self.get_user_profile(user_id)
        
        if "experience_level" in preferences:
            profile.experience_level = UserExperienceLevel(preferences["experience_level"])
        
        if "preferred_topics" in preferences:
            profile.preferred_topics = preferences["preferred_topics"]
        
        if "favorite_cryptocurrencies" in preferences:
            profile.favorite_cryptocurrencies = preferences["favorite_cryptocurrencies"]
        
        if "trading_style" in preferences:
            profile.trading_style = preferences["trading_style"]
        
        if "risk_tolerance" in preferences:
            profile.risk_tolerance = preferences["risk_tolerance"]
        
        if "preferred_response_style" in preferences:
            profile.preferred_response_style = preferences["preferred_response_style"]
        
        if "timezone" in preferences:
            profile.timezone = preferences["timezone"]
        
        if "language" in preferences:
            profile.language = preferences["language"]
        
        await self._save_user_profile(profile)
    
    async def get_contextual_suggestions(self, user_id: int, current_intent: str) -> List[str]:
        """Get contextual suggestions based on conversation history"""
        profile = await self.get_user_profile(user_id)
        recent_messages = list(self.short_term_memory[user_id])
        
        suggestions = []
        
        # Based on current intent
        if current_intent == "get_realtime_price":
            if profile.favorite_cryptocurrencies:
                suggestions.extend([f"Check {crypto} price" for crypto in profile.favorite_cryptocurrencies[:3]])
            suggestions.append("Compare with yesterday's price")
            suggestions.append("Set price alert")
        
        elif current_intent == "analyze_portfolio":
            suggestions.extend([
                "Portfolio optimization suggestions",
                "Risk analysis",
                "Performance comparison",
                "Rebalancing recommendations"
            ])
        
        elif current_intent == "find_yield_opportunities":
            suggestions.extend([
                "Compare APY rates",
                "Risk assessment",
                "Protocol security analysis",
                "Impermanent loss calculator"
            ])
        
        # Based on conversation flow
        if len(recent_messages) > 1:
            last_intent = recent_messages[-1].intent
            if last_intent == "get_realtime_price" and current_intent != "get_realtime_price":
                suggestions.append("Check another crypto price")
        
        # Based on user experience level
        if profile.experience_level == UserExperienceLevel.BEGINNER:
            suggestions.extend([
                "Explain crypto basics",
                "What is DeFi?",
                "How to start investing?"
            ])
        elif profile.experience_level == UserExperienceLevel.ADVANCED:
            suggestions.extend([
                "Technical analysis",
                "Advanced trading strategies",
                "DeFi protocol comparison"
            ])
        
        return suggestions[:5]  # Return top 5 suggestions
    
    async def learn_from_feedback(self, user_id: int, message_id: str, feedback_score: float, feedback_text: Optional[str] = None):
        """Learn from user feedback to improve responses"""
        # Update message feedback
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE conversation_messages 
                    SET feedback_score = ? 
                    WHERE message_id = ?
                """, (feedback_score, message_id))
        except Exception as e:
            logger.error(f"Error updating feedback: {e}")
        
        # Update user satisfaction score
        profile = await self.get_user_profile(user_id)
        profile.satisfaction_score = (profile.satisfaction_score * 0.9) + (feedback_score * 0.1)
        await self._save_user_profile(profile)
        
        # Learn from negative feedback
        if feedback_score < 0.3 and feedback_text:
            await self._analyze_negative_feedback(user_id, feedback_text)
    
    async def _update_user_profile(self, message: ConversationMessage):
        """Update user profile based on message"""
        profile = await self.get_user_profile(message.user_id)
        
        profile.interaction_count += 1
        profile.last_interaction = message.timestamp
        
        # Update common questions
        if message.intent and message.intent not in profile.common_questions:
            profile.common_questions.append(message.intent)
            if len(profile.common_questions) > 10:
                profile.common_questions = profile.common_questions[-10:]
        
        # Extract favorite cryptocurrencies from entities
        for entity in message.entities:
            if entity.get('type') == 'cryptocurrency':
                crypto = entity.get('normalized_value')
                if crypto and crypto not in profile.favorite_cryptocurrencies:
                    profile.favorite_cryptocurrencies.append(crypto)
                    if len(profile.favorite_cryptocurrencies) > 10:
                        profile.favorite_cryptocurrencies = profile.favorite_cryptocurrencies[-10:]
        
        # Infer experience level from interaction patterns
        if profile.interaction_count > 50 and profile.experience_level == UserExperienceLevel.BEGINNER:
            profile.experience_level = UserExperienceLevel.INTERMEDIATE
        elif profile.interaction_count > 200 and profile.experience_level == UserExperienceLevel.INTERMEDIATE:
            profile.experience_level = UserExperienceLevel.ADVANCED
        
        await self._save_user_profile(profile)
    
    async def _update_topic_contexts(self, message: ConversationMessage):
        """Update topic contexts based on message"""
        if not message.intent:
            return
        
        user_id = message.user_id
        topic = self._extract_topic_from_intent(message.intent)
        
        if user_id not in self.topic_contexts:
            self.topic_contexts[user_id] = {}
        
        if topic not in self.topic_contexts[user_id]:
            self.topic_contexts[user_id][topic] = TopicContext(
                topic=topic,
                mentioned_entities={},
                last_mentioned=message.timestamp,
                user_interest_score=1.0,
                related_topics=[],
                common_questions=[]
            )
        
        topic_context = self.topic_contexts[user_id][topic]
        topic_context.last_mentioned = message.timestamp
        topic_context.user_interest_score += 0.1
        
        # Update mentioned entities
        for entity in message.entities:
            entity_key = f"{entity.get('type')}:{entity.get('value')}"
            topic_context.mentioned_entities[entity_key] = topic_context.mentioned_entities.get(entity_key, 0) + 1
        
        # Update common questions
        if message.intent not in topic_context.common_questions:
            topic_context.common_questions.append(message.intent)
            if len(topic_context.common_questions) > 5:
                topic_context.common_questions = topic_context.common_questions[-5:]
        
        # Store in database
        await self._save_topic_context(user_id, topic_context)
    
    def _extract_topic_from_intent(self, intent: str) -> str:
        """Extract topic from intent name"""
        topic_mapping = {
            "get_realtime_price": "price_tracking",
            "get_historical_price": "price_tracking",
            "analyze_price_movement": "market_analysis",
            "analyze_portfolio": "portfolio_management",
            "add_to_portfolio": "portfolio_management",
            "remove_from_portfolio": "portfolio_management",
            "optimize_portfolio": "portfolio_management",
            "get_trading_advice": "trading",
            "entry_exit_strategy": "trading",
            "risk_management_advice": "risk_management",
            "find_yield_opportunities": "defi_yield",
            "liquidity_pool_analysis": "defi_yield",
            "defi_protocol_security": "defi_security",
            "technical_analysis_request": "technical_analysis",
            "support_resistance_levels": "technical_analysis",
            "market_sentiment_analysis": "market_sentiment",
            "compare_cryptocurrencies": "market_analysis",
            "create_price_alert": "alerts",
            "manage_alerts": "alerts",
            "crypto_news_analysis": "news",
            "social_sentiment_analysis": "social_sentiment",
            "crypto_concept_explanation": "education",
        }
        
        return topic_mapping.get(intent, "general")
    
    async def _analyze_conversation_patterns(self, user_id: int) -> Dict[str, Any]:
        """Analyze conversation patterns for a user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT intent, COUNT(*) as count, AVG(response_time) as avg_response_time,
                           AVG(CASE WHEN feedback_score IS NOT NULL THEN feedback_score ELSE 0.5 END) as avg_feedback
                    FROM conversation_messages 
                    WHERE user_id = ? AND timestamp > datetime('now', '-30 days')
                    GROUP BY intent
                    ORDER BY count DESC
                """, (user_id,))
                
                patterns = {
                    "most_common_intents": [],
                    "avg_response_times": {},
                    "satisfaction_by_intent": {},
                    "interaction_frequency": 0
                }
                
                for row in cursor.fetchall():
                    intent, count, avg_time, avg_feedback = row
                    patterns["most_common_intents"].append({"intent": intent, "count": count})
                    patterns["avg_response_times"][intent] = avg_time
                    patterns["satisfaction_by_intent"][intent] = avg_feedback
                
                # Calculate interaction frequency
                cursor = conn.execute("""
                    SELECT COUNT(*) FROM conversation_messages 
                    WHERE user_id = ? AND timestamp > datetime('now', '-7 days')
                """, (user_id,))
                
                weekly_count = cursor.fetchone()[0]
                patterns["interaction_frequency"] = weekly_count / 7  # per day
                
                return patterns
                
        except Exception as e:
            logger.error(f"Error analyzing conversation patterns: {e}")
            return {}
    
    async def _get_recommended_topics(self, user_id: int) -> List[str]:
        """Get recommended topics based on user history"""
        profile = await self.get_user_profile(user_id)
        patterns = await self._analyze_conversation_patterns(user_id)
        
        recommendations = []
        
        # Based on common intents
        common_intents = patterns.get("most_common_intents", [])
        for intent_data in common_intents[:3]:
            intent = intent_data["intent"]
            topic = self._extract_topic_from_intent(intent)
            if topic not in recommendations:
                recommendations.append(topic)
        
        # Based on experience level
        if profile.experience_level == UserExperienceLevel.BEGINNER:
            recommendations.extend(["education", "basic_trading", "portfolio_basics"])
        elif profile.experience_level == UserExperienceLevel.ADVANCED:
            recommendations.extend(["technical_analysis", "defi_advanced", "trading_strategies"])
        
        # Based on favorite cryptocurrencies
        if profile.favorite_cryptocurrencies:
            recommendations.append("price_tracking")
            recommendations.append("market_analysis")
        
        return list(set(recommendations))[:5]
    
    async def _get_personalization_hints(self, user_id: int) -> Dict[str, Any]:
        """Get personalization hints for response adaptation"""
        profile = await self.get_user_profile(user_id)
        patterns = await self._analyze_conversation_patterns(user_id)
        
        hints = {
            "response_style": profile.preferred_response_style,
            "experience_level": profile.experience_level.value,
            "interaction_frequency": patterns.get("interaction_frequency", 0),
            "satisfaction_score": profile.satisfaction_score,
            "preferred_topics": profile.preferred_topics,
            "favorite_cryptos": profile.favorite_cryptocurrencies,
            "common_questions": profile.common_questions,
            "avoided_topics": profile.avoided_topics,
            "timezone": profile.timezone,
            "language": profile.language
        }
        
        return hints
    
    async def _infer_session_goals(self, session: SessionContext, intent: str, entities: List[Dict]):
        """Infer user goals for the current session"""
        goal_mapping = {
            "get_realtime_price": "price_monitoring",
            "analyze_portfolio": "portfolio_review",
            "find_yield_opportunities": "yield_optimization",
            "get_trading_advice": "trading_decision",
            "technical_analysis_request": "market_analysis",
            "create_price_alert": "alert_setup",
            "crypto_concept_explanation": "learning"
        }
        
        goal = goal_mapping.get(intent)
        if goal and goal not in session.session_goals:
            session.session_goals.append(goal)
    
    async def _save_user_profile(self, profile: UserProfile):
        """Save user profile to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO user_profiles 
                    (user_id, username, experience_level, preferred_topics, favorite_cryptocurrencies,
                     trading_style, risk_tolerance, preferred_response_style, timezone, language,
                     interaction_count, first_interaction, last_interaction, satisfaction_score,
                     common_questions, avoided_topics)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    profile.user_id,
                    profile.username,
                    profile.experience_level.value,
                    json.dumps(profile.preferred_topics),
                    json.dumps(profile.favorite_cryptocurrencies),
                    profile.trading_style,
                    profile.risk_tolerance,
                    profile.preferred_response_style,
                    profile.timezone,
                    profile.language,
                    profile.interaction_count,
                    profile.first_interaction.isoformat(),
                    profile.last_interaction.isoformat(),
                    profile.satisfaction_score,
                    json.dumps(profile.common_questions),
                    json.dumps(profile.avoided_topics)
                ))
        except Exception as e:
            logger.error(f"Error saving user profile: {e}")
    
    async def _save_topic_context(self, user_id: int, topic_context: TopicContext):
        """Save topic context to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO topic_contexts 
                    (user_id, topic, mentioned_entities, last_mentioned, user_interest_score,
                     related_topics, common_questions)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    topic_context.topic,
                    json.dumps(topic_context.mentioned_entities),
                    topic_context.last_mentioned.isoformat(),
                    topic_context.user_interest_score,
                    json.dumps(topic_context.related_topics),
                    json.dumps(topic_context.common_questions)
                ))
        except Exception as e:
            logger.error(f"Error saving topic context: {e}")
    
    async def _store_session_context(self, session: SessionContext):
        """Store session context in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO session_contexts 
                    (session_id, user_id, start_time, last_activity, current_topic,
                     topic_history, mentioned_entities, conversation_flow, user_mood,
                     session_goals, unresolved_questions)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session.session_id,
                    session.user_id,
                    session.start_time.isoformat(),
                    session.last_activity.isoformat(),
                    session.current_topic,
                    json.dumps(session.topic_history),
                    json.dumps(session.mentioned_entities),
                    json.dumps(session.conversation_flow),
                    session.user_mood,
                    json.dumps(session.session_goals),
                    json.dumps(session.unresolved_questions)
                ))
        except Exception as e:
            logger.error(f"Error storing session context: {e}")
    
    async def _analyze_negative_feedback(self, user_id: int, feedback_text: str):
        """Analyze negative feedback to improve responses"""
        profile = await self.get_user_profile(user_id)
        
        # Simple keyword analysis for improvement areas
        if "too technical" in feedback_text.lower():
            profile.preferred_response_style = "concise"
        elif "too simple" in feedback_text.lower():
            profile.preferred_response_style = "technical"
        elif "slow" in feedback_text.lower():
            # Note: improve response time for this user
            pass
        elif "wrong" in feedback_text.lower() or "incorrect" in feedback_text.lower():
            # Note: improve accuracy for this user's queries
            pass
        
        await self._save_user_profile(profile)

# Global instance
conversation_memory = ConversationMemorySystem()

async def get_conversation_context(user_id: int, session_id: Optional[str] = None) -> Dict[str, Any]:
    """Get conversation context for a user"""
    return await conversation_memory.get_conversation_context(user_id, session_id)

async def store_conversation_message(message: ConversationMessage):
    """Store a conversation message"""
    await conversation_memory.store_message(message)

async def update_user_preferences(user_id: int, preferences: Dict[str, Any]):
    """Update user preferences"""
    await conversation_memory.update_user_preferences(user_id, preferences)

async def get_contextual_suggestions(user_id: int, current_intent: str) -> List[str]:
    """Get contextual suggestions"""
    return await conversation_memory.get_contextual_suggestions(user_id, current_intent)

async def learn_from_feedback(user_id: int, message_id: str, feedback_score: float, feedback_text: Optional[str] = None):
    """Learn from user feedback"""
    await conversation_memory.learn_from_feedback(user_id, message_id, feedback_score, feedback_text)