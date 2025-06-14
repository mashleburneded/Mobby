# src/user_db.py
import sqlite3
import logging
import time
import json
from cryptography.fernet import Fernet
from config import config

DB_FILE = 'data/user_data.sqlite'
logger = logging.getLogger(__name__)

try:
    fernet = Fernet(config.get('BOT_MASTER_ENCRYPTION_KEY').encode())
except Exception as e:
    logger.critical(f"Could not initialize database encryptor: {e}")
    fernet = None

class UserDatabase:
    """User database management class"""
    
    def __init__(self):
        self.db_file = DB_FILE
        self.fernet = fernet
        logger.info("User database initialized with proper schema and indexes.")

def init_db(db_path=None):
    db_file = db_path or DB_FILE
    con = sqlite3.connect(db_file)
    cur = con.cursor()
    
    # Enable foreign key constraints
    cur.execute("PRAGMA foreign_keys = ON")
    
    # Create tables with proper foreign key relationships
    cur.execute('''CREATE TABLE IF NOT EXISTS user_properties (
        user_id INTEGER, 
        key TEXT, 
        value TEXT, 
        PRIMARY KEY (user_id, key)
    )''')
    
    cur.execute('''CREATE TABLE IF NOT EXISTS username_map (
        user_id INTEGER PRIMARY KEY, 
        username TEXT, 
        last_seen INTEGER
    )''')
    
    cur.execute('''CREATE TABLE IF NOT EXISTS onchain_alerts (
        alert_id TEXT PRIMARY KEY, 
        user_id INTEGER NOT NULL, 
        chat_id INTEGER NOT NULL, 
        alert_type TEXT NOT NULL, 
        params TEXT NOT NULL, 
        created_at INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES user_properties (user_id) ON DELETE CASCADE
    )''')
    
    # Create indexes for better performance
    cur.execute('''CREATE INDEX IF NOT EXISTS idx_user_properties_user_id ON user_properties(user_id)''')
    cur.execute('''CREATE INDEX IF NOT EXISTS idx_username_map_username ON username_map(username)''')
    cur.execute('''CREATE INDEX IF NOT EXISTS idx_onchain_alerts_user_id ON onchain_alerts(user_id)''')
    cur.execute('''CREATE INDEX IF NOT EXISTS idx_onchain_alerts_created_at ON onchain_alerts(created_at)''')
    
    con.commit()
    con.close()
    logger.info("User database initialized with proper schema and indexes.")

def update_username_mapping(user_id: int, username: str):
    if not username: return
    con = sqlite3.connect(DB_FILE); cur = con.cursor()
    cur.execute("INSERT OR REPLACE INTO username_map (user_id, username, last_seen) VALUES (?, ?, ?)", (user_id, username, int(time.time())))
    con.commit(); con.close()

def get_user_id_from_username(username: str) -> int | None:
    con = sqlite3.connect(DB_FILE); cur = con.cursor()
    res = cur.execute("SELECT user_id FROM username_map WHERE username = ?", (username,)); result = res.fetchone()
    con.close(); return result[0] if result else None

def set_user_property(user_id: int, key: str, value: str, encrypted: bool = False):
    if encrypted and not fernet: logger.error(f"Cannot set encrypted property '{key}': Encryptor unavailable."); return
    final_value = fernet.encrypt(value.encode()).decode() if encrypted else value
    
    # Retry logic for database operations
    for attempt in range(3):
        try:
            con = sqlite3.connect(DB_FILE, timeout=10.0)
            con.execute("PRAGMA busy_timeout = 10000")  # 10 second timeout
            cur = con.cursor()
            cur.execute("INSERT OR REPLACE INTO user_properties (user_id, key, value) VALUES (?, ?, ?)", (user_id, key, final_value))
            con.commit()
            con.close()
            return
        except sqlite3.OperationalError as e:
            if attempt < 2:  # Retry up to 3 times
                time.sleep(0.1 * (attempt + 1))  # Exponential backoff
                continue
            else:
                logger.error(f"Database operation failed after 3 attempts: {e}")
                if 'con' in locals():
                    con.close()
        except Exception as e:
            logger.error(f"Unexpected database error: {e}")
            if 'con' in locals():
                con.close()
            break

def get_user_property(user_id: int, key: str, default=None, encrypted: bool = False):
    if encrypted and not fernet: 
        logger.error(f"Cannot get encrypted property '{key}': Encryptor unavailable.")
        return default
    
    # Retry logic for database operations
    for attempt in range(3):
        try:
            con = sqlite3.connect(DB_FILE, timeout=10.0)
            con.execute("PRAGMA busy_timeout = 10000")  # 10 second timeout
            cur = con.cursor()
            res = cur.execute("SELECT value FROM user_properties WHERE user_id = ? AND key = ?", (user_id, key))
            result = res.fetchone()
            con.close()
            
            if not result: 
                return default
            
            value = result[0]
            if encrypted:
                try: 
                    return fernet.decrypt(value.encode()).decode()
                except Exception as e: 
                    logger.error(f"Failed to decrypt property '{key}' for user {user_id}: {e}")
                    return default
            return value
            
        except sqlite3.OperationalError as e:
            if attempt < 2:  # Retry up to 3 times
                time.sleep(0.1 * (attempt + 1))  # Exponential backoff
                continue
            else:
                logger.error(f"Database read operation failed after 3 attempts: {e}")
                if 'con' in locals():
                    con.close()
                return default
        except Exception as e:
            logger.error(f"Unexpected database error: {e}")
            if 'con' in locals():
                con.close()
            return default

def add_alert_to_db(arkham_alert_id: str, user_id: int, chat_id: int, alert_type: str, params: dict):
    con = sqlite3.connect(DB_FILE); cur = con.cursor()
    cur.execute("INSERT INTO onchain_alerts (alert_id, user_id, chat_id, alert_type, params, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (arkham_alert_id, user_id, chat_id, alert_type, json.dumps(params), int(time.time())))
    con.commit(); con.close()

def count_user_alerts(user_id: int) -> int:
    con = sqlite3.connect(DB_FILE); cur = con.cursor()
    res = cur.execute("SELECT COUNT(*) FROM onchain_alerts WHERE user_id = ?", (user_id,)); count = res.fetchone()[0]
    con.close(); return count