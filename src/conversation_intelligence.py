# src/conversation_intelligence.py
"""
Advanced Conversation Intelligence for Möbius AI Assistant
Handles real-time conversation streaming, learning, and context management
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import sqlite3
import threading
from pathlib import Path
from cryptography.fernet import Fernet
from config import config

logger = logging.getLogger(__name__)

@dataclass
class ConversationMessage:
    """Represents a conversation message"""
    message_id: str
    user_id: int
    username: str
    chat_id: int
    chat_type: str
    text: str
    timestamp: datetime
    is_bot_message: bool = False
    reply_to_message_id: Optional[str] = None
    entities: Optional[Dict[str, Any]] = field(default_factory=dict)
    sentiment: Optional[str] = None
    topics: Optional[List[str]] = field(default_factory=list)

@dataclass
class ConversationContext:
    """Conversation context for a chat"""
    chat_id: int
    participants: Set[int]
    message_count: int
    last_activity: datetime
    active_topics: List[str]
    sentiment_trend: List[str]
    key_entities: Dict[str, int]
    conversation_flow: List[str]
    summary_points: List[str]

@dataclass
class LearningInsight:
    """Learning insight from conversation analysis"""
    insight_type: str
    content: str
    confidence: float
    timestamp: datetime
    related_users: List[int]
    related_topics: List[str]

class ConversationIntelligence:
    """
    Advanced conversation intelligence system that:
    1. Streams and processes conversations in real-time
    2. Learns from user interactions
    3. Maintains context across conversations
    4. Generates intelligent summaries
    5. Provides reinforcement learning feedback
    """
    
    def __init__(self, db_path: str = "data/conversation_intelligence.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        
        # In-memory conversation state
        self.active_conversations: Dict[int, ConversationContext] = {}
        self.message_buffer: Dict[int, deque] = defaultdict(lambda: deque(maxlen=100))
        self.learning_insights: List[LearningInsight] = []
        
        # Streaming and processing
        self.message_queue = asyncio.Queue()
        self.processing_tasks: Set[asyncio.Task] = set()
        self.is_streaming = False
        
        # Learning parameters
        self.learning_config = {
            "min_confidence_threshold": 0.6,
            "context_window_size": 10,
            "summary_trigger_threshold": 20,  # messages
            "learning_rate": 0.1,
            "topic_extraction_enabled": True,
            "sentiment_analysis_enabled": True,
            "entity_recognition_enabled": True
        }
        
        # Initialize encryption for message storage
        self._init_encryption()
        
        # Initialize database
        self._init_database()
        
        # Start background processing
        self._start_background_processing()
    
    def _init_encryption(self):
        """Initialize encryption for secure message storage"""
        try:
            # Try to get the master encryption key from config
            encryption_key = config.get('BOT_MASTER_ENCRYPTION_KEY')
            if encryption_key:
                # Ensure the key is properly formatted for Fernet
                if len(encryption_key.encode()) == 32:
                    # If it's exactly 32 bytes, use it directly
                    self.fernet = Fernet(encryption_key.encode())
                else:
                    # If it's a different length, derive a proper key
                    from cryptography.hazmat.primitives import hashes
                    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
                    import base64
                    
                    # Use PBKDF2 to derive a proper 32-byte key
                    kdf = PBKDF2HMAC(
                        algorithm=hashes.SHA256(),
                        length=32,
                        salt=b'conversation_intelligence_salt',
                        iterations=100000,
                    )
                    key = base64.urlsafe_b64encode(kdf.derive(encryption_key.encode()))
                    self.fernet = Fernet(key)
                
                logger.info("✅ Conversation Intelligence: Encryption initialized with master key")
            else:
                # Fallback: Generate a session-specific key (less secure but functional)
                logger.warning("⚠️ No master encryption key found, generating session key")
                session_key = Fernet.generate_key()
                self.fernet = Fernet(session_key)
                logger.warning("⚠️ Using session-only encryption - messages will not persist across restarts")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize encryption: {e}")
            # Fallback to no encryption (not recommended for production)
            self.fernet = None
            logger.critical("❌ SECURITY WARNING: Message storage will be UNENCRYPTED!")
    
    def _encrypt_text(self, text: str) -> str:
        """Encrypt text for secure storage"""
        if self.fernet and text:
            try:
                encrypted_bytes = self.fernet.encrypt(text.encode('utf-8'))
                return encrypted_bytes.decode('utf-8')
            except Exception as e:
                logger.error(f"Encryption failed: {e}")
                return text  # Fallback to plain text
        return text
    
    def _decrypt_text(self, encrypted_text: str) -> str:
        """Decrypt text from storage"""
        if self.fernet and encrypted_text:
            try:
                decrypted_bytes = self.fernet.decrypt(encrypted_text.encode('utf-8'))
                return decrypted_bytes.decode('utf-8')
            except Exception as e:
                logger.error(f"Decryption failed: {e}")
                return encrypted_text  # Fallback to returning as-is
        return encrypted_text
    
    async def start_streaming(self):
        """Start conversation streaming and processing"""
        if not self.is_streaming:
            self.is_streaming = True
            
            # Start message processing task
            loop = asyncio.get_event_loop()
            task = loop.create_task(self._process_message_queue())
            self.processing_tasks.add(task)
            
            # Start periodic summary generation
            summary_task = loop.create_task(self._periodic_summary_generation())
            self.processing_tasks.add(summary_task)
            
            logger.info("✅ Conversation intelligence streaming started")
    
    def _init_database(self):
        """Initialize SQLite database for conversation storage"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS conversations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        chat_id INTEGER NOT NULL,
                        message_id TEXT NOT NULL,
                        user_id INTEGER NOT NULL,
                        username TEXT,
                        text TEXT NOT NULL,
                        timestamp DATETIME NOT NULL,
                        is_bot_message BOOLEAN DEFAULT FALSE,
                        reply_to_message_id TEXT,
                        entities TEXT,
                        sentiment TEXT,
                        topics TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS conversation_contexts (
                        chat_id INTEGER PRIMARY KEY,
                        participants TEXT NOT NULL,
                        message_count INTEGER DEFAULT 0,
                        last_activity DATETIME NOT NULL,
                        active_topics TEXT,
                        sentiment_trend TEXT,
                        key_entities TEXT,
                        conversation_flow TEXT,
                        summary_points TEXT,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS learning_insights (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        chat_id INTEGER,
                        period_hours INTEGER,
                        insights_data TEXT,
                        generated_at TEXT,
                        insight_type TEXT NOT NULL,
                        content TEXT NOT NULL,
                        confidence REAL NOT NULL,
                        timestamp DATETIME NOT NULL,
                        related_users TEXT,
                        related_topics TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS chat_summaries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        chat_id INTEGER NOT NULL,
                        period_hours INTEGER,
                        summary_data TEXT,
                        generated_at TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create indexes for performance
                conn.execute("CREATE INDEX IF NOT EXISTS idx_conversations_chat_id ON conversations(chat_id)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_conversations_timestamp ON conversations(timestamp)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id)")
                
                logger.info("Conversation intelligence database initialized")
                
        except Exception as e:
            logger.error(f"Failed to initialize conversation database: {e}")
    
    def _start_background_processing(self):
        """Start background processing tasks"""
        try:
            # Start message processing task
            loop = asyncio.get_event_loop()
            task = loop.create_task(self._process_message_queue())
            self.processing_tasks.add(task)
            
            # Start periodic summary generation
            summary_task = loop.create_task(self._periodic_summary_generation())
            self.processing_tasks.add(summary_task) # FIXED: Added summary_task instead of task
            
            self.is_streaming = True
            logger.info("Background conversation processing started")
            
        except Exception as e:
            logger.error(f"Failed to start background processing: {e}")
    
    async def stream_message(self, message: ConversationMessage):
        """Stream a new message for processing"""
        try:
            # Add to queue for processing
            await self.message_queue.put(message)
            
            # Update in-memory buffer
            self.message_buffer[message.chat_id].append(message)
            
            # Update conversation context
            await self._update_conversation_context(message)
            
        except Exception as e:
            logger.error(f"Error streaming message: {e}")
    
    async def _process_message_queue(self):
        """Process messages from the queue"""
        while self.is_streaming:
            try:
                # Get message from queue with timeout
                message = await asyncio.wait_for(
                    self.message_queue.get(), 
                    timeout=1.0
                )
                
                # Process the message
                await self._process_single_message(message)
                
                # Mark task as done
                self.message_queue.task_done()
                
            except asyncio.TimeoutError:
                # No messages to process, continue
                continue
            except Exception as e:
                logger.error(f"Error processing message queue: {e}")
                await asyncio.sleep(1)
    
    async def _process_single_message(self, message: ConversationMessage):
        """Process a single message for learning and insights"""
        try:
            # Store in database
            await self._store_message(message)
            
            # Extract entities and topics
            if self.learning_config["entity_recognition_enabled"]:
                message.entities = self._extract_entities(message.text)
            
            if self.learning_config["topic_extraction_enabled"]:
                message.topics = self._extract_topics(message.text)
            
            # Analyze sentiment
            if self.learning_config["sentiment_analysis_enabled"]:
                message.sentiment = self._analyze_sentiment(message.text)
            
            # Generate learning insights
            insights = await self._generate_learning_insights(message)
            for insight in insights:
                await self._store_learning_insight(insight)
            
            # Check if summary should be generated
            await self._check_summary_trigger(message.chat_id)
            
        except Exception as e:
            logger.error(f"Error processing single message: {e}")
    
    async def _store_message(self, message: ConversationMessage):
        """Store message in database with encryption"""
        try:
            # Encrypt sensitive data before storage
            encrypted_text = self._encrypt_text(message.text)
            encrypted_username = self._encrypt_text(message.username) if message.username else None
            
            # Encrypt entities and topics if they exist
            encrypted_entities = None
            if message.entities:
                entities_json = json.dumps(message.entities)
                encrypted_entities = self._encrypt_text(entities_json)
            
            encrypted_topics = None
            if message.topics:
                topics_json = json.dumps(message.topics)
                encrypted_topics = self._encrypt_text(topics_json)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO conversations 
                    (chat_id, message_id, user_id, username, text, timestamp, 
                     is_bot_message, reply_to_message_id, entities, sentiment, topics)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    message.chat_id,
                    message.message_id,
                    message.user_id,
                    encrypted_username,
                    encrypted_text,
                    message.timestamp,
                    message.is_bot_message,
                    message.reply_to_message_id,
                    encrypted_entities,
                    message.sentiment,  # Sentiment is not sensitive (just positive/negative/neutral)
                    encrypted_topics
                ))
                
            logger.debug(f"✅ Message stored with encryption for chat {message.chat_id}")
                
        except Exception as e:
            logger.error(f"Error storing encrypted message: {e}")
    
    async def _update_conversation_context(self, message: ConversationMessage):
        """Update conversation context with new message"""
        try:
            chat_id = message.chat_id
            
            # Get or create context
            if chat_id not in self.active_conversations:
                self.active_conversations[chat_id] = ConversationContext(
                    chat_id=chat_id,
                    participants=set(),
                    message_count=0,
                    last_activity=message.timestamp,
                    active_topics=[],
                    sentiment_trend=[],
                    key_entities={},
                    conversation_flow=[],
                    summary_points=[]
                )
            
            context = self.active_conversations[chat_id]
            
            # Update context
            context.participants.add(message.user_id)
            context.message_count += 1
            context.last_activity = message.timestamp
            
            # Update topics
            if message.topics:
                for topic in message.topics:
                    if topic not in context.active_topics:
                        context.active_topics.append(topic)
                    # Keep only recent topics
                    if len(context.active_topics) > 10:
                        context.active_topics = context.active_topics[-10:]
            
            # Update sentiment trend
            if message.sentiment:
                context.sentiment_trend.append(message.sentiment)
                if len(context.sentiment_trend) > 20:
                    context.sentiment_trend = context.sentiment_trend[-20:]
            
            # Update entities
            if message.entities:
                for entity, value in message.entities.items():
                    if entity in context.key_entities:
                        context.key_entities[entity] += 1
                    else:
                        context.key_entities[entity] = 1
            
            # Update conversation flow
            flow_item = f"{message.username}: {message.text[:50]}..."
            context.conversation_flow.append(flow_item)
            if len(context.conversation_flow) > 15:
                context.conversation_flow = context.conversation_flow[-15:]
            
            # Store context in database
            await self._store_conversation_context(context)
            
        except Exception as e:
            logger.error(f"Error updating conversation context: {e}")
    
    async def _store_conversation_context(self, context: ConversationContext):
        """Store conversation context in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO conversation_contexts
                    (chat_id, participants, message_count, last_activity, 
                     active_topics, sentiment_trend, key_entities, 
                     conversation_flow, summary_points, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    context.chat_id,
                    json.dumps(list(context.participants)),
                    context.message_count,
                    context.last_activity,
                    json.dumps(context.active_topics),
                    json.dumps(context.sentiment_trend),
                    json.dumps(context.key_entities),
                    json.dumps(context.conversation_flow),
                    json.dumps(context.summary_points),
                    datetime.now()
                ))
                
        except Exception as e:
            logger.error(f"Error storing conversation context: {e}")
    
    def _extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract entities from text"""
        entities = {}
        
        # Crypto symbols
        crypto_pattern = r'\b(BTC|ETH|SOL|ADA|DOT|LINK|UNI|AAVE|MATIC|AVAX|ATOM|NEAR|FTM|ALGO|XRP|LTC|BCH|ETC|XLM|VET|THETA|TFUEL|HBAR|ICP|FIL|EOS|TRX|XTZ|DASH|ZEC|QTUM|ONT|ZIL|RVN|DGB|SC|DCR|LSK|ARDR|STRAT|WAVES|NXT|BURST|XEM|MONA|DOGE|SHIB)\b'
        import re
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
        
        # URLs
        url_pattern = r'https?://[^\s]+'
        url_matches = re.findall(url_pattern, text)
        if url_matches:
            entities["urls"] = url_matches
        
        return entities
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract topics from text"""
        topics = []
        text_lower = text.lower()
        
        # Crypto topics
        crypto_topics = {
            "defi": ["defi", "decentralized finance", "yield farming", "liquidity"],
            "trading": ["trading", "buy", "sell", "swap", "exchange"],
            "market": ["market", "price", "pump", "dump", "bull", "bear"],
            "technology": ["blockchain", "smart contract", "consensus", "mining"],
            "nft": ["nft", "non-fungible", "opensea", "collectible"],
            "staking": ["staking", "validator", "rewards", "delegation"]
        }
        
        for topic, keywords in crypto_topics.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)
        
        return topics
    
    def _analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment of text (simplified implementation)"""
        text_lower = text.lower()
        
        positive_words = ["good", "great", "awesome", "amazing", "bullish", "moon", "pump", "up", "high", "profit", "gain", "win"]
        negative_words = ["bad", "terrible", "awful", "bearish", "dump", "down", "low", "loss", "lose", "crash", "rekt"]
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    async def _generate_learning_insights(self, message: ConversationMessage) -> List[LearningInsight]:
        """Generate learning insights from message"""
        insights = []
        
        try:
            # User behavior insights
            if message.entities and "crypto_symbols" in message.entities:
                insight = LearningInsight(
                    insight_type="user_interest",
                    content=f"User {message.username} shows interest in {', '.join(message.entities['crypto_symbols'])}",
                    confidence=0.8,
                    timestamp=message.timestamp,
                    related_users=[message.user_id],
                    related_topics=message.topics or []
                )
                insights.append(insight)
            
            # Conversation pattern insights
            if message.chat_id in self.active_conversations:
                context = self.active_conversations[message.chat_id]
                if context.message_count % 10 == 0:  # Every 10 messages
                    insight = LearningInsight(
                        insight_type="conversation_pattern",
                        content=f"Active discussion in chat {message.chat_id} with {len(context.participants)} participants",
                        confidence=0.7,
                        timestamp=message.timestamp,
                        related_users=list(context.participants),
                        related_topics=context.active_topics
                    )
                    insights.append(insight)
            
            # Sentiment insights
            if message.sentiment and message.sentiment != "neutral":
                insight = LearningInsight(
                    insight_type="sentiment_trend",
                    content=f"User {message.username} expressed {message.sentiment} sentiment",
                    confidence=0.6,
                    timestamp=message.timestamp,
                    related_users=[message.user_id],
                    related_topics=message.topics or []
                )
                insights.append(insight)
            
        except Exception as e:
            logger.error(f"Error generating learning insights: {e}")
        
        return insights
    
    async def _store_learning_insight(self, insight: LearningInsight):
        """Store learning insight in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO learning_insights
                    (insight_type, content, confidence, timestamp, related_users, related_topics)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    insight.insight_type,
                    insight.content,
                    insight.confidence,
                    insight.timestamp,
                    json.dumps(insight.related_users),
                    json.dumps(insight.related_topics)
                ))
                
        except Exception as e:
            logger.error(f"Error storing learning insight: {e}")
    
    async def _check_summary_trigger(self, chat_id: int):
        """Check if summary should be generated for chat"""
        try:
            if chat_id in self.active_conversations:
                context = self.active_conversations[chat_id]
                
                # Trigger summary every N messages
                threshold = self.learning_config["summary_trigger_threshold"]
                if context.message_count > 0 and context.message_count % threshold == 0:
                    logger.info(f"Triggering summary for chat {chat_id} at message count {context.message_count}")
                    await self._generate_conversation_summary(chat_id)
                    
        except Exception as e:
            logger.error(f"Error checking summary trigger: {e}")
    
    async def _generate_conversation_summary(self, chat_id: int):
        """Generate conversation summary for chat"""
        try:
            # Get recent messages
            messages = await self._get_recent_messages(chat_id, limit=50)
            
            if not messages:
                return
            
            # Generate summary points
            summary_points = []
            
            # Key topics discussed
            all_topics = []
            for msg in messages:
                if msg.topics:
                    all_topics.extend(msg.topics)
            
            if all_topics:
                topic_counts = {}
                for topic in all_topics:
                    topic_counts[topic] = topic_counts.get(topic, 0) + 1
                
                top_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:3]
                summary_points.append(f"Main topics: {', '.join([topic for topic, _ in top_topics])}")
            
            # Sentiment analysis
            sentiments = [msg.sentiment for msg in messages if msg.sentiment]
            if sentiments:
                positive_count = sentiments.count("positive")
                negative_count = sentiments.count("negative")
                neutral_count = sentiments.count("neutral")
                
                if positive_count > negative_count:
                    summary_points.append("Overall sentiment: Positive")
                elif negative_count > positive_count:
                    summary_points.append("Overall sentiment: Negative")
                else:
                    summary_points.append("Overall sentiment: Neutral")
            
            # Active participants
            participants = set(msg.user_id for msg in messages)
            summary_points.append(f"Active participants: {len(participants)}")
            
            # Update context with summary
            if chat_id in self.active_conversations:
                self.active_conversations[chat_id].summary_points = summary_points
                await self._store_conversation_context(self.active_conversations[chat_id])
            
            logger.info(f"Generated summary for chat {chat_id}: {summary_points}")
            
        except Exception as e:
            logger.error(f"Error generating conversation summary: {e}")
    
    async def _get_recent_messages(self, chat_id: int, limit: int = 50) -> List[ConversationMessage]:
        """Get recent messages for a chat"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT message_id, user_id, username, text, timestamp, 
                           is_bot_message, reply_to_message_id, entities, sentiment, topics
                    FROM conversations
                    WHERE chat_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (chat_id, limit))
                
                messages = []
                for row in cursor.fetchall():
                    # Decrypt sensitive data
                    decrypted_username = self._decrypt_text(row[2]) if row[2] else None
                    decrypted_text = self._decrypt_text(row[3])
                    
                    # Decrypt entities and topics
                    entities = None
                    if row[7]:
                        decrypted_entities = self._decrypt_text(row[7])
                        try:
                            entities = json.loads(decrypted_entities)
                        except json.JSONDecodeError as json_e:
                            logger.error(f"JSONDecodeError for entities in chat {chat_id}, message {row[0]}: {json_e}. Raw decrypted: {decrypted_entities[:100]}...")
                            entities = None
                    
                    topics = None
                    if row[9]:
                        decrypted_topics = self._decrypt_text(row[9])
                        try:
                            topics = json.loads(decrypted_topics)
                        except json.JSONDecodeError as json_e:
                            logger.error(f"JSONDecodeError for topics in chat {chat_id}, message {row[0]}: {json_e}. Raw decrypted: {decrypted_topics[:100]}...")
                            topics = None
                    
                    message = ConversationMessage(
                        message_id=row[0],
                        user_id=row[1],
                        username=decrypted_username,
                        chat_id=chat_id,
                        chat_type="unknown",  # Not stored in this query
                        text=decrypted_text,
                        timestamp=datetime.fromisoformat(row[4]),
                        is_bot_message=bool(row[5]),
                        reply_to_message_id=row[6],
                        entities=entities,
                        sentiment=row[8],
                        topics=topics
                    )
                    messages.append(message)
                
                return messages
                
        except Exception as e:
            logger.error(f"Error getting recent messages: {e}")
            return []
    
    async def _periodic_summary_generation(self):
        """Periodically generate summaries for active chats"""
        while self.is_streaming:
            try:
                # Wait for 1 hour
                await asyncio.sleep(3600)
                
                # Generate summaries for active chats
                current_time = datetime.now()
                for chat_id, context in self.active_conversations.items():
                    # Generate summary if chat has been active in last hour
                    if current_time - context.last_activity < timedelta(hours=1):
                        await self._generate_conversation_summary(chat_id)
                
            except Exception as e:
                logger.error(f"Error in periodic summary generation: {e}")
    
    async def get_conversation_summary(self, chat_id: int, hours: int = 24) -> Dict[str, Any]:
        """Get conversation summary for a chat"""
        try:
            # Get context
            context = self.active_conversations.get(chat_id)
            if not context:
                return {"error": "No conversation context found"}
            
            # Get recent messages
            since_time = datetime.now() - timedelta(hours=hours)
            messages = await self._get_messages_since(chat_id, since_time)
            
            # Generate comprehensive summary
            summary = {
                "chat_id": chat_id,
                "time_period": f"Last {hours} hours",
                "message_count": len(messages),
                "participants": len(context.participants),
                "active_topics": context.active_topics,
                "sentiment_trend": context.sentiment_trend[-10:],  # Last 10 sentiments
                "key_entities": context.key_entities,
                "summary_points": context.summary_points,
                "last_activity": context.last_activity.isoformat()
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting conversation summary: {e}")
            return {"error": str(e)}
    
    async def _get_messages_since(self, chat_id: int, since_time: datetime) -> List[ConversationMessage]:
        """Get messages since a specific time"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT message_id, user_id, username, text, timestamp, 
                           is_bot_message, reply_to_message_id, entities, sentiment, topics
                    FROM conversations
                    WHERE chat_id = ? AND timestamp >= ?
                    ORDER BY timestamp ASC
                """, (chat_id, since_time))
                
                messages = []
                for row in cursor.fetchall():
                    # Decrypt sensitive data
                    decrypted_username = self._decrypt_text(row[2]) if row[2] else None
                    decrypted_text = self._decrypt_text(row[3])
                    
                    # Decrypt entities and topics
                    entities = None
                    if row[7]:
                        decrypted_entities = self._decrypt_text(row[7])
                        try:
                            entities = json.loads(decrypted_entities)
                        except json.JSONDecodeError as json_e:
                            logger.error(f"JSONDecodeError for entities in chat {chat_id}, message {row[0]}: {json_e}. Raw decrypted: {decrypted_entities[:100]}...")
                            entities = None
                    
                    topics = None
                    if row[9]:
                        decrypted_topics = self._decrypt_text(row[9])
                        try:
                            topics = json.loads(decrypted_topics)
                        except json.JSONDecodeError as json_e:
                            logger.error(f"JSONDecodeError for topics in chat {chat_id}, message {row[0]}: {json_e}. Raw decrypted: {decrypted_topics[:100]}...")
                            topics = None
                    
                    message = ConversationMessage(
                        message_id=row[0],
                        user_id=row[1],
                        username=decrypted_username,
                        chat_id=chat_id,
                        chat_type="unknown",
                        text=decrypted_text,
                        timestamp=datetime.fromisoformat(row[4]),
                        is_bot_message=bool(row[5]),
                        reply_to_message_id=row[6],
                        entities=entities,
                        sentiment=row[8],
                        topics=topics
                    )
                    messages.append(message)
                
                return messages
                
        except Exception as e:
            logger.error(f"Error getting messages since time: {e}")
            return []
    
    async def get_learning_insights(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent learning insights"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT insight_type, content, confidence, timestamp, 
                           related_users, related_topics
                    FROM learning_insights
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (limit,))
                
                insights = []
                for row in cursor.fetchall():
                    insight = {
                        "insight_type": row[0],
                        "content": row[1],
                        "confidence": row[2],
                        "timestamp": row[3],
                        "related_users": json.loads(row[4]) if row[4] else [],
                        "related_topics": json.loads(row[5]) if row[5] else []
                    }
                    insights.append(insight)
                
                return insights
                
        except Exception as e:
            logger.error(f"Error getting learning insights: {e}")
            return []
    
    def stop_streaming(self):
        """Stop conversation streaming and processing"""
        self.is_streaming = False
        
        # Cancel all processing tasks
        for task in self.processing_tasks:
            task.cancel()
        
        logger.info("Conversation intelligence streaming stopped")

# Global instance
conversation_intelligence = ConversationIntelligence()

# Export functions
async def stream_conversation_message(
    message_id: str,
    user_id: int,
    username: str,
    chat_id: int,
    chat_type: str,
    text: str,
    is_bot_message: bool = False,
    reply_to_message_id: Optional[str] = None
):
    """Stream a conversation message for processing"""
    message = ConversationMessage(
        message_id=message_id,
        user_id=user_id,
        username=username,
        chat_id=chat_id,
        chat_type=chat_type,
        text=text,
        timestamp=datetime.now(),
        is_bot_message=is_bot_message,
        reply_to_message_id=reply_to_message_id
    )
    
    await conversation_intelligence.stream_message(message)

async def get_chat_summary(chat_id: int, hours: int = 24) -> Dict[str, Any]:
    """Get conversation summary for a chat"""
    return await conversation_intelligence.get_conversation_summary(chat_id, hours)

async def get_recent_insights(limit: int = 50) -> List[Dict[str, Any]]:
    """Get recent learning insights"""
    return await conversation_intelligence.get_learning_insights(limit)

async def get_learning_insights(chat_id: int, hours: int = 24) -> Dict[str, Any]:
    """Get learning insights for a chat"""
    try:
        # Use the global conversation intelligence instance
        global conversation_intelligence
        
        # Get messages from the last N hours
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with sqlite3.connect(conversation_intelligence.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT text, username, timestamp 
                FROM conversations 
                WHERE chat_id = ? AND timestamp > ?
                ORDER BY timestamp DESC
            """, (chat_id, cutoff_time.isoformat()))
            
            messages = cursor.fetchall()
        
        if not messages:
            return {
                "chat_id": chat_id,
                "period_hours": hours,
                "insights": [],
                "topics": [],
                "sentiment": "neutral",
                "activity_level": "low"
            }
        
        # Decrypt and analyze messages for insights
        message_texts = []
        for msg in messages:
            decrypted_text = conversation_intelligence._decrypt_text(msg[0])
            message_texts.append(decrypted_text)
        all_text = " ".join(message_texts).lower()
        
        # Topic extraction
        crypto_topics = []
        if "bitcoin" in all_text or "btc" in all_text:
            crypto_topics.append("Bitcoin")
        if "ethereum" in all_text or "eth" in all_text:
            crypto_topics.append("Ethereum")
        if "trading" in all_text:
            crypto_topics.append("Trading")
        if "defi" in all_text:
            crypto_topics.append("DeFi")
        
        # Sentiment analysis (simple)
        positive_words = ["good", "great", "bullish", "up", "profit", "gain"]
        negative_words = ["bad", "bearish", "down", "loss", "crash", "dump"]
        
        positive_count = sum(1 for word in positive_words if word in all_text)
        negative_count = sum(1 for word in negative_words if word in all_text)
        
        if positive_count > negative_count:
            sentiment = "positive"
        elif negative_count > positive_count:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        # Activity level
        if len(messages) > 50:
            activity_level = "high"
        elif len(messages) > 20:
            activity_level = "medium"
        else:
            activity_level = "low"
        
        # Generate insights
        insights = []
        if crypto_topics:
            insights.append(f"Main discussion topics: {', '.join(crypto_topics)}")
        if sentiment != "neutral":
            insights.append(f"Overall sentiment is {sentiment}")
        insights.append(f"Activity level is {activity_level} with {len(messages)} messages")
        
        learning_data = {
            "chat_id": chat_id,
            "period_hours": hours,
            "insights": insights,
            "topics": crypto_topics,
            "sentiment": sentiment,
            "activity_level": activity_level,
            "message_count": len(messages),
            "generated_at": datetime.now().isoformat()
        }
        
        return learning_data
        
    except Exception as e:
        logger.error(f"Error generating learning insights: {e}")
        return {
            "chat_id": chat_id,
            "period_hours": hours,
            "insights": [f"Error generating insights: {e}"],
            "topics": [],
            "sentiment": "neutral",
            "activity_level": "low"
        }
