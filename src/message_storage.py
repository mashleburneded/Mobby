# src/message_storage.py
"""
Persistent Message Storage System with Encryption
Stores all chat messages in encrypted format for later summarization
"""

import sqlite3
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
from encryption import encrypt_message, decrypt_message

logger = logging.getLogger(__name__)

class MessageStorage:
    """Persistent storage for encrypted chat messages"""
    
    def __init__(self, db_path: str = "data/messages.db"):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize the message storage database"""
        Path(self.db_path).parent.mkdir(exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Messages table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id INTEGER NOT NULL,
                    chat_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    username TEXT,
                    encrypted_text TEXT,
                    message_type TEXT DEFAULT 'text',
                    timestamp REAL NOT NULL,
                    date_created TEXT NOT NULL,
                    is_edit BOOLEAN DEFAULT FALSE,
                    is_deleted BOOLEAN DEFAULT FALSE,
                    reply_to_message_id INTEGER,
                    forward_from_chat_id INTEGER,
                    media_file_id TEXT,
                    media_caption TEXT
                )
            ''')
            
            # Chat metadata table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_metadata (
                    chat_id INTEGER PRIMARY KEY,
                    chat_title TEXT,
                    chat_type TEXT,
                    member_count INTEGER,
                    last_message_time REAL,
                    total_messages INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')
            
            # User activity table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_activity (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_seen TEXT NOT NULL,
                    last_seen TEXT NOT NULL,
                    total_messages INTEGER DEFAULT 0,
                    last_chat_id INTEGER
                )
            ''')
            
            # Daily summaries table (kept for 7 days for security)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_summaries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER NOT NULL,
                    summary_date TEXT NOT NULL,
                    summary_text TEXT NOT NULL,
                    message_count INTEGER DEFAULT 0,
                    participant_count INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    UNIQUE(chat_id, summary_date)
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_chat_timestamp ON messages(chat_id, timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_user_timestamp ON messages(user_id, timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_date_created ON messages(date_created)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_summaries_chat_date ON daily_summaries(chat_id, summary_date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_summaries_created_at ON daily_summaries(created_at)')
            
            conn.commit()
            logger.info("Message storage database initialized")
    
    def store_message(self, message_data: Dict[str, Any]) -> bool:
        """Store a message with encryption"""
        try:
            # Encrypt the message text
            text_to_encrypt = str(message_data.get('text', ''))
            encrypted_text = encrypt_message(text_to_encrypt)
            
            if not encrypted_text:
                logger.warning("Failed to encrypt message, storing as plaintext")
                encrypted_text = text_to_encrypt
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Store the message
                cursor.execute('''
                    INSERT INTO messages 
                    (message_id, chat_id, user_id, username, encrypted_text, 
                     message_type, timestamp, date_created, is_edit, is_deleted,
                     reply_to_message_id, forward_from_chat_id, media_file_id, media_caption)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    message_data.get('message_id'),
                    message_data.get('chat_id'),
                    message_data.get('user_id'),
                    message_data.get('username'),
                    encrypted_text,
                    message_data.get('message_type', 'text'),
                    message_data.get('timestamp'),
                    datetime.now().isoformat(),
                    message_data.get('is_edit', False),
                    message_data.get('is_deleted', False),
                    message_data.get('reply_to_message_id'),
                    message_data.get('forward_from_chat_id'),
                    message_data.get('media_file_id'),
                    message_data.get('media_caption')
                ))
                
                # Update chat metadata
                self._update_chat_metadata(cursor, message_data)
                
                # Update user activity
                self._update_user_activity(cursor, message_data)
                
                conn.commit()
                logger.debug(f"Stored encrypted message from user {message_data.get('user_id')} in chat {message_data.get('chat_id')}")
                return True
                
        except Exception as e:
            logger.error(f"Error storing message: {e}")
            return False
    
    def _update_chat_metadata(self, cursor, message_data: Dict[str, Any]):
        """Update chat metadata"""
        chat_id = message_data.get('chat_id')
        timestamp = message_data.get('timestamp')
        
        cursor.execute('''
            INSERT OR REPLACE INTO chat_metadata 
            (chat_id, last_message_time, total_messages, created_at, updated_at)
            VALUES (
                ?, ?, 
                COALESCE((SELECT total_messages FROM chat_metadata WHERE chat_id = ?), 0) + 1,
                COALESCE((SELECT created_at FROM chat_metadata WHERE chat_id = ?), ?),
                ?
            )
        ''', (chat_id, timestamp, chat_id, chat_id, datetime.now().isoformat(), datetime.now().isoformat()))
    
    def _update_user_activity(self, cursor, message_data: Dict[str, Any]):
        """Update user activity"""
        user_id = message_data.get('user_id')
        username = message_data.get('username')
        chat_id = message_data.get('chat_id')
        now = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_activity 
            (user_id, username, first_seen, last_seen, total_messages, last_chat_id)
            VALUES (
                ?, ?, 
                COALESCE((SELECT first_seen FROM user_activity WHERE user_id = ?), ?),
                ?,
                COALESCE((SELECT total_messages FROM user_activity WHERE user_id = ?), 0) + 1,
                ?
            )
        ''', (user_id, username, user_id, now, now, user_id, chat_id))
    
    def get_messages_for_period(self, chat_id: int, hours: int = 24) -> List[Dict[str, Any]]:
        """Get and decrypt messages for a specific time period"""
        try:
            cutoff_time = time.time() - (hours * 3600)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT message_id, chat_id, user_id, username, encrypted_text,
                           message_type, timestamp, is_edit, is_deleted,
                           reply_to_message_id, media_caption
                    FROM messages 
                    WHERE chat_id = ? AND timestamp >= ?
                    ORDER BY timestamp ASC
                ''', (chat_id, cutoff_time))
                
                messages = []
                for row in cursor.fetchall():
                    message_data = {
                        'message_id': row[0],
                        'chat_id': row[1],
                        'user_id': row[2],
                        'username': row[3],
                        'encrypted_text': row[4],
                        'message_type': row[5],
                        'timestamp': row[6],
                        'is_edit': row[7],
                        'is_deleted': row[8],
                        'reply_to_message_id': row[9],
                        'media_caption': row[10]
                    }
                    
                    # Decrypt the message
                    decrypted_text = decrypt_message(message_data['encrypted_text'])
                    if decrypted_text:
                        message_data['text'] = decrypted_text
                    else:
                        # Fallback to encrypted text if decryption fails
                        message_data['text'] = message_data['encrypted_text']
                    
                    messages.append(message_data)
                
                logger.info(f"Retrieved {len(messages)} messages for chat {chat_id} from last {hours} hours")
                return messages
                
        except Exception as e:
            logger.error(f"Error retrieving messages: {e}")
            return []
    
    def get_chat_statistics(self, chat_id: int) -> Dict[str, Any]:
        """Get statistics for a chat"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get basic stats
                cursor.execute('''
                    SELECT COUNT(*) as total_messages,
                           COUNT(DISTINCT user_id) as unique_users,
                           MIN(timestamp) as first_message,
                           MAX(timestamp) as last_message
                    FROM messages WHERE chat_id = ?
                ''', (chat_id,))
                
                stats = cursor.fetchone()
                
                # Get top users
                cursor.execute('''
                    SELECT username, COUNT(*) as message_count
                    FROM messages 
                    WHERE chat_id = ? AND username IS NOT NULL
                    GROUP BY user_id, username
                    ORDER BY message_count DESC
                    LIMIT 5
                ''', (chat_id,))
                
                top_users = cursor.fetchall()
                
                # Get message types distribution
                cursor.execute('''
                    SELECT message_type, COUNT(*) as count
                    FROM messages 
                    WHERE chat_id = ?
                    GROUP BY message_type
                ''', (chat_id,))
                
                message_types = cursor.fetchall()
                
                return {
                    'total_messages': stats[0] if stats else 0,
                    'unique_users': stats[1] if stats else 0,
                    'first_message': datetime.fromtimestamp(stats[2]).isoformat() if stats and stats[2] else None,
                    'last_message': datetime.fromtimestamp(stats[3]).isoformat() if stats and stats[3] else None,
                    'top_users': [{'username': u[0], 'count': u[1]} for u in top_users],
                    'message_types': [{'type': t[0], 'count': t[1]} for t in message_types]
                }
                
        except Exception as e:
            logger.error(f"Error getting chat statistics: {e}")
            return {}
    
    def cleanup_old_messages(self, hours: int = 24):
        """Clean up messages older than specified hours for security"""
        try:
            cutoff_time = time.time() - (hours * 3600)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Count messages to be deleted
                cursor.execute('SELECT COUNT(*) FROM messages WHERE timestamp < ?', (cutoff_time,))
                count = cursor.fetchone()[0]
                
                # Delete old messages for security
                cursor.execute('DELETE FROM messages WHERE timestamp < ?', (cutoff_time,))
                
                conn.commit()
                logger.info(f"🔒 Security cleanup: Deleted {count} messages older than {hours} hours")
                
        except Exception as e:
            logger.error(f"Error cleaning up old messages: {e}")
    
    def auto_security_cleanup(self):
        """Automatic security cleanup - delete messages after 24 hours"""
        self.cleanup_old_messages(hours=24)
        self.cleanup_old_summaries(days=7)
        logger.info("🔒 Automatic security cleanup completed - all messages older than 24 hours deleted")
    
    def store_daily_summary(self, chat_id: int, summary_text: str, message_count: int = 0, participant_count: int = 0) -> bool:
        """Store daily summary (kept for 7 days)"""
        try:
            summary_date = datetime.now().strftime('%Y-%m-%d')
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO daily_summaries 
                    (chat_id, summary_date, summary_text, message_count, participant_count, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    chat_id,
                    summary_date,
                    summary_text,
                    message_count,
                    participant_count,
                    datetime.now().isoformat()
                ))
                
                conn.commit()
                logger.info(f"📝 Stored daily summary for chat {chat_id} on {summary_date}")
                return True
                
        except Exception as e:
            logger.error(f"Error storing daily summary: {e}")
            return False
    
    def get_recent_summaries(self, chat_id: int, days: int = 7) -> List[Dict[str, Any]]:
        """Get recent daily summaries for a chat"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT summary_date, summary_text, message_count, participant_count, created_at
                    FROM daily_summaries 
                    WHERE chat_id = ? AND summary_date >= ?
                    ORDER BY summary_date DESC
                ''', (chat_id, cutoff_date))
                
                summaries = []
                for row in cursor.fetchall():
                    summaries.append({
                        'date': row[0],
                        'summary': row[1],
                        'message_count': row[2],
                        'participant_count': row[3],
                        'created_at': row[4]
                    })
                
                return summaries
                
        except Exception as e:
            logger.error(f"Error retrieving summaries: {e}")
            return []
    
    def cleanup_old_summaries(self, days: int = 7):
        """Clean up summaries older than specified days"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Count summaries to be deleted
                cursor.execute('SELECT COUNT(*) FROM daily_summaries WHERE summary_date < ?', (cutoff_date,))
                count = cursor.fetchone()[0]
                
                # Delete old summaries
                cursor.execute('DELETE FROM daily_summaries WHERE summary_date < ?', (cutoff_date,))
                
                conn.commit()
                logger.info(f"🔒 Security cleanup: Deleted {count} summaries older than {days} days")
                
        except Exception as e:
            logger.error(f"Error cleaning up old summaries: {e}")
    
    def export_chat_messages(self, chat_id: int, hours: int = 24) -> str:
        """Export chat messages as formatted text"""
        try:
            messages = self.get_messages_for_period(chat_id, hours)
            
            if not messages:
                return "No messages found for the specified period."
            
            export_lines = []
            export_lines.append(f"Chat Export - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            export_lines.append(f"Chat ID: {chat_id}")
            export_lines.append(f"Period: Last {hours} hours")
            export_lines.append(f"Total Messages: {len(messages)}")
            export_lines.append("-" * 50)
            
            for msg in messages:
                timestamp = datetime.fromtimestamp(msg['timestamp']).strftime('%H:%M:%S')
                username = msg.get('username', 'Unknown')
                text = msg.get('text', '')
                
                if msg.get('is_edit'):
                    export_lines.append(f"[{timestamp}] {username} (edited): {text}")
                elif msg.get('is_deleted'):
                    export_lines.append(f"[{timestamp}] {username} (deleted message)")
                elif msg.get('message_type') != 'text':
                    export_lines.append(f"[{timestamp}] {username} [{msg['message_type']}]: {text}")
                else:
                    export_lines.append(f"[{timestamp}] {username}: {text}")
            
            return "\n".join(export_lines)
            
        except Exception as e:
            logger.error(f"Error exporting messages: {e}")
            return f"Error exporting messages: {e}"

# Global instance
message_storage = MessageStorage()