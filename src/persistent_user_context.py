# src/persistent_user_context.py
"""
Persistent User Context and Preferences Manager
Maintains user preferences, conversation context, and learning data separately from message storage
"""

import json
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class UserPreference:
    key: str
    value: Any
    learned_from: str  # 'explicit' or 'conversation'
    confidence: float
    last_updated: datetime
    usage_count: int = 0

@dataclass
class ConversationContext:
    user_id: int
    current_topic: Optional[str] = None
    last_intent: Optional[str] = None
    conversation_flow: List[Dict] = None
    active_session: bool = True
    session_start: datetime = None
    last_activity: datetime = None
    preferences: Dict[str, UserPreference] = None
    
    def __post_init__(self):
        if self.conversation_flow is None:
            self.conversation_flow = []
        if self.session_start is None:
            self.session_start = datetime.now()
        if self.last_activity is None:
            self.last_activity = datetime.now()
        if self.preferences is None:
            self.preferences = {}

class PersistentUserContext:
    """Manages persistent user context and preferences"""
    
    def __init__(self, db_path: str = "data/user_context.db"):
        self.db_path = db_path
        self.init_database()
        logger.info("✅ User context database initialized")
    
    def init_database(self):
        """Initialize the user context database"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    user_id INTEGER,
                    key TEXT,
                    value TEXT,
                    learned_from TEXT,
                    confidence REAL,
                    last_updated TEXT,
                    usage_count INTEGER DEFAULT 0,
                    PRIMARY KEY (user_id, key)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversation_context (
                    user_id INTEGER PRIMARY KEY,
                    current_topic TEXT,
                    last_intent TEXT,
                    conversation_flow TEXT,
                    session_start TEXT,
                    last_activity TEXT
                )
            """)
            
            conn.commit()

class PersistentUserContextManager:
    """Manages user context and preferences with persistent storage"""
    
    def __init__(self, db_path: str = "data/user_context.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self.active_contexts: Dict[int, ConversationContext] = {}
        self.init_database()
    
    def init_database(self):
        """Initialize the user context database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS user_preferences (
                        user_id INTEGER,
                        key TEXT,
                        value TEXT,
                        learned_from TEXT,
                        confidence REAL,
                        last_updated TEXT,
                        usage_count INTEGER DEFAULT 0,
                        PRIMARY KEY (user_id, key)
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS conversation_context (
                        user_id INTEGER PRIMARY KEY,
                        current_topic TEXT,
                        last_intent TEXT,
                        conversation_flow TEXT,
                        session_start TEXT,
                        last_activity TEXT
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS user_corrections (
                        user_id INTEGER,
                        original_input TEXT,
                        corrected_input TEXT,
                        correction_type TEXT,
                        timestamp TEXT
                    )
                """)
                
                logger.info("✅ User context database initialized")
        except Exception as e:
            logger.error(f"Failed to initialize user context database: {e}")
    
    def get_user_context(self, user_id: int) -> ConversationContext:
        """Get or create user context"""
        if user_id not in self.active_contexts:
            # Load from database
            context = self.load_user_context(user_id)
            if not context:
                context = ConversationContext(user_id=user_id)
            
            # Load preferences
            context.preferences = self.load_user_preferences(user_id)
            self.active_contexts[user_id] = context
        
        return self.active_contexts[user_id]
    
    def load_user_context(self, user_id: int) -> Optional[ConversationContext]:
        """Load user context from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT current_topic, last_intent, conversation_flow, session_start, last_activity "
                    "FROM conversation_context WHERE user_id = ?",
                    (user_id,)
                )
                row = cursor.fetchone()
                
                if row:
                    current_topic, last_intent, conversation_flow_json, session_start_str, last_activity_str = row
                    
                    conversation_flow = json.loads(conversation_flow_json) if conversation_flow_json else []
                    session_start = datetime.fromisoformat(session_start_str) if session_start_str else datetime.now()
                    
                    # Check if session is still active (within 24 hours)
                    last_activity = datetime.fromisoformat(last_activity_str) if last_activity_str else datetime.now()
                    active_session = (datetime.now() - last_activity) < timedelta(hours=24)
                    
                    return ConversationContext(
                        user_id=user_id,
                        current_topic=current_topic,
                        last_intent=last_intent,
                        conversation_flow=conversation_flow,
                        active_session=active_session,
                        session_start=session_start
                    )
        except Exception as e:
            logger.error(f"Failed to load user context for {user_id}: {e}")
        
        return None
    
    def load_user_preferences(self, user_id: int) -> Dict[str, UserPreference]:
        """Load user preferences from database"""
        preferences = {}
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT key, value, learned_from, confidence, last_updated, usage_count "
                    "FROM user_preferences WHERE user_id = ?",
                    (user_id,)
                )
                
                for row in cursor.fetchall():
                    key, value_json, learned_from, confidence, last_updated_str, usage_count = row
                    
                    try:
                        value = json.loads(value_json)
                        last_updated = datetime.fromisoformat(last_updated_str)
                        
                        preferences[key] = UserPreference(
                            key=key,
                            value=value,
                            learned_from=learned_from,
                            confidence=confidence,
                            last_updated=last_updated,
                            usage_count=usage_count
                        )
                    except Exception as e:
                        logger.error(f"Failed to parse preference {key} for user {user_id}: {e}")
        
        except Exception as e:
            logger.error(f"Failed to load preferences for user {user_id}: {e}")
        
        return preferences
    
    def save_user_context(self, context: ConversationContext):
        """Save user context to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO conversation_context 
                    (user_id, current_topic, last_intent, conversation_flow, session_start, last_activity)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    context.user_id,
                    context.current_topic,
                    context.last_intent,
                    json.dumps(context.conversation_flow),
                    context.session_start.isoformat(),
                    datetime.now().isoformat()
                ))
        except Exception as e:
            logger.error(f"Failed to save user context for {context.user_id}: {e}")
    
    def save_user_preference(self, user_id: int, preference: UserPreference):
        """Save user preference to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO user_preferences 
                    (user_id, key, value, learned_from, confidence, last_updated, usage_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    preference.key,
                    json.dumps(preference.value),
                    preference.learned_from,
                    preference.confidence,
                    preference.last_updated.isoformat(),
                    preference.usage_count
                ))
        except Exception as e:
            logger.error(f"Failed to save preference {preference.key} for user {user_id}: {e}")
    
    def learn_preference(self, user_id: int, key: str, value: Any, source: str = "conversation", confidence: float = 0.7):
        """Learn a user preference from conversation"""
        context = self.get_user_context(user_id)
        
        # Check if preference already exists
        if key in context.preferences:
            existing = context.preferences[key]
            # Update if new confidence is higher or it's an explicit setting
            if confidence > existing.confidence or source == "explicit":
                existing.value = value
                existing.confidence = confidence
                existing.learned_from = source
                existing.last_updated = datetime.now()
                existing.usage_count += 1
        else:
            # Create new preference
            preference = UserPreference(
                key=key,
                value=value,
                learned_from=source,
                confidence=confidence,
                last_updated=datetime.now(),
                usage_count=1
            )
            context.preferences[key] = preference
        
        # Save to database
        self.save_user_preference(user_id, context.preferences[key])
        logger.info(f"Learned preference for user {user_id}: {key} = {value} (confidence: {confidence})")
    
    def get_preference(self, user_id: int, key: str, default: Any = None) -> Any:
        """Get user preference with usage tracking"""
        context = self.get_user_context(user_id)
        
        if key in context.preferences:
            preference = context.preferences[key]
            preference.usage_count += 1
            preference.last_updated = datetime.now()
            self.save_user_preference(user_id, preference)
            return preference.value
        
        return default
    
    def update_conversation_flow(self, user_id: int, message_type: str, content: str, intent: str = None):
        """Update conversation flow with real-time context"""
        context = self.get_user_context(user_id)
        
        # Add to conversation flow
        flow_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": message_type,  # 'user_message', 'bot_response', 'intent_detected'
            "content": content,
            "intent": intent
        }
        
        context.conversation_flow.append(flow_entry)
        
        # Keep only last 20 entries for performance
        context.conversation_flow = context.conversation_flow[-20:]
        
        # Update context
        if intent:
            context.last_intent = intent
        
        # Save to database
        self.save_user_context(context)
    
    def analyze_conversation_patterns(self, user_id: int) -> Dict[str, Any]:
        """Analyze user conversation patterns to learn preferences"""
        context = self.get_user_context(user_id)
        
        patterns = {
            "frequent_intents": {},
            "preferred_topics": {},
            "communication_style": "professional",
            "active_times": [],
            "response_preferences": {}
        }
        
        # Analyze conversation flow
        for entry in context.conversation_flow:
            if entry.get("intent"):
                intent = entry["intent"]
                patterns["frequent_intents"][intent] = patterns["frequent_intents"].get(intent, 0) + 1
            
            # Analyze communication style
            content = entry.get("content", "").lower()
            if any(word in content for word in ["please", "thank you", "could you"]):
                patterns["communication_style"] = "polite"
            elif any(word in content for word in ["hey", "yo", "sup"]):
                patterns["communication_style"] = "casual"
        
        return patterns
    
    def save_correction(self, user_id: int, original: str, corrected: str, correction_type: str):
        """Save user corrections for learning"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO user_corrections 
                    (user_id, original_input, corrected_input, correction_type, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, (user_id, original, corrected, correction_type, datetime.now().isoformat()))
        except Exception as e:
            logger.error(f"Failed to save correction for user {user_id}: {e}")
    
    def get_user_corrections(self, user_id: int) -> List[Dict]:
        """Get user's correction history"""
        corrections = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT original_input, corrected_input, correction_type, timestamp
                    FROM user_corrections 
                    WHERE user_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT 50
                """, (user_id,))
                
                for row in cursor.fetchall():
                    corrections.append({
                        "original": row[0],
                        "corrected": row[1],
                        "type": row[2],
                        "timestamp": row[3]
                    })
        except Exception as e:
            logger.error(f"Failed to get corrections for user {user_id}: {e}")
        
        return corrections
    
    def cleanup_old_data(self, days: int = 30):
        """Clean up old conversation data while preserving preferences"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            with sqlite3.connect(self.db_path) as conn:
                # Clean old conversation contexts
                conn.execute("""
                    DELETE FROM conversation_context 
                    WHERE last_activity < ?
                """, (cutoff_date.isoformat(),))
                
                # Clean old corrections
                conn.execute("""
                    DELETE FROM user_corrections 
                    WHERE timestamp < ?
                """, (cutoff_date.isoformat(),))
                
                # Keep preferences but clean very old unused ones
                old_cutoff = datetime.now() - timedelta(days=90)
                conn.execute("""
                    DELETE FROM user_preferences 
                    WHERE last_updated < ? AND usage_count < 2
                """, (old_cutoff.isoformat(),))
                
            logger.info(f"Cleaned up user context data older than {days} days")
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")

# Global instance
user_context_manager = PersistentUserContextManager()