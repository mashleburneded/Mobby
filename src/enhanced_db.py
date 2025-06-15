# src/enhanced_db.py
"""
Enhanced database layer for Möbius AI Assistant.
Implements connection pooling, indexing, query optimization, and migration support.
"""
import sqlite3
import threading
import time
import logging
from typing import Dict, List, Optional, Any, Union
from contextlib import contextmanager
from dataclasses import dataclass
import json
from queue import Queue, Empty
from cryptography.fernet import Fernet
import os
from config import config

logger = logging.getLogger(__name__)

@dataclass
class QueryResult:
    """Query result container with metadata"""
    data: Any
    execution_time: float
    rows_affected: int = 0
    success: bool = True
    error: Optional[str] = None

class ConnectionPool:
    """
    Thread-safe SQLite connection pool with automatic cleanup.
    Provides efficient database access with connection reuse.
    """
    
    def __init__(self, database_path: str, pool_size: int = 10, timeout: float = 30.0):
        self.database_path = database_path
        self.pool_size = pool_size
        self.timeout = timeout
        self._pool = Queue(maxsize=pool_size)
        self._lock = threading.RLock()
        self._created_connections = 0
        
        # Initialize pool with connections
        self._initialize_pool()
        
        logger.info(f"Database connection pool initialized with {pool_size} connections")
    
    def _initialize_pool(self):
        """Initialize the connection pool"""
        for _ in range(self.pool_size):
            conn = self._create_connection()
            if conn:
                self._pool.put(conn)
    
    def _create_connection(self) -> Optional[sqlite3.Connection]:
        """Create a new database connection with optimizations"""
        try:
            conn = sqlite3.connect(
                self.database_path,
                timeout=self.timeout,
                check_same_thread=False
            )
            
            # Enable WAL mode for better concurrency
            conn.execute("PRAGMA journal_mode=WAL")
            
            # Optimize for performance
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=10000")
            conn.execute("PRAGMA temp_store=MEMORY")
            
            # Enable foreign keys
            conn.execute("PRAGMA foreign_keys=ON")
            
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            
            with self._lock:
                self._created_connections += 1
            
            return conn
        except Exception as e:
            logger.error(f"Failed to create database connection: {e}")
            return None
    
    @contextmanager
    def get_connection(self):
        """Get a connection from the pool"""
        conn = None
        try:
            # Try to get connection from pool
            try:
                conn = self._pool.get(timeout=5.0)
            except Empty:
                # Pool is empty, create new connection
                conn = self._create_connection()
                if not conn:
                    raise Exception("Failed to create database connection")
            
            # Test connection
            conn.execute("SELECT 1")
            
            yield conn
            
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            if conn:
                try:
                    conn.close()
                except:
                    pass
                conn = None
            raise
        finally:
            # Return connection to pool
            if conn:
                try:
                    # Reset connection state
                    conn.rollback()
                    self._pool.put(conn, timeout=1.0)
                except:
                    # Connection is bad, close it
                    try:
                        conn.close()
                    except:
                        pass
    
    def close_all(self):
        """Close all connections in the pool"""
        with self._lock:
            while not self._pool.empty():
                try:
                    conn = self._pool.get_nowait()
                    conn.close()
                except:
                    pass

class EnhancedDatabase:
    """
    Enhanced database interface with security, performance, and reliability features.
    Provides encrypted storage, query optimization, and comprehensive error handling.
    """
    
    def __init__(self, db_path: str = 'data/user_data.sqlite'):
        self.db_path = db_path
        self.pool = ConnectionPool(db_path)
        
        # Initialize encryption
        try:
            encryption_key = config.get('BOT_MASTER_ENCRYPTION_KEY')
            self.fernet = Fernet(encryption_key.encode()) if encryption_key else None
        except Exception as e:
            logger.error(f"Failed to initialize database encryption: {e}")
            self.fernet = None
        
        # Query cache for frequently accessed data
        self._query_cache: Dict[str, Any] = {}
        self._cache_ttl: Dict[str, float] = {}
        self._cache_timeout = 300  # 5 minutes
        
        # Initialize database schema
        self._initialize_schema()
        
        logger.info("Enhanced database initialized")
    
    def _initialize_schema(self):
        """Initialize database schema with indexes and optimizations"""
        schema_queries = [
            # User properties table with index
            """CREATE TABLE IF NOT EXISTS user_properties (
                user_id INTEGER NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                encrypted BOOLEAN DEFAULT FALSE,
                created_at INTEGER DEFAULT (strftime('%s', 'now')),
                updated_at INTEGER DEFAULT (strftime('%s', 'now')),
                PRIMARY KEY (user_id, key)
            )""",
            
            # Username mapping with index
            """CREATE TABLE IF NOT EXISTS username_map (
                user_id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                last_seen INTEGER NOT NULL,
                created_at INTEGER DEFAULT (strftime('%s', 'now'))
            )""",
            
            # Enhanced alerts table
            """CREATE TABLE IF NOT EXISTS onchain_alerts (
                alert_id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                chat_id INTEGER NOT NULL,
                alert_type TEXT NOT NULL,
                params TEXT NOT NULL,
                active BOOLEAN DEFAULT TRUE,
                triggered_count INTEGER DEFAULT 0,
                last_triggered INTEGER,
                created_at INTEGER NOT NULL,
                updated_at INTEGER DEFAULT (strftime('%s', 'now')),
                FOREIGN KEY (user_id) REFERENCES user_properties(user_id)
            )""",
            
            # User sessions for security tracking
            """CREATE TABLE IF NOT EXISTS user_sessions (
                session_id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                ip_hash TEXT,
                user_agent_hash TEXT,
                created_at INTEGER NOT NULL,
                last_activity INTEGER NOT NULL,
                expires_at INTEGER NOT NULL,
                active BOOLEAN DEFAULT TRUE
            )""",
            
            # Analytics and metrics
            """CREATE TABLE IF NOT EXISTS command_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                command TEXT NOT NULL,
                execution_time REAL NOT NULL,
                success BOOLEAN NOT NULL,
                error_type TEXT,
                timestamp INTEGER NOT NULL
            )""",
            
            # Audit log for security events
            """CREATE TABLE IF NOT EXISTS security_audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                event_type TEXT NOT NULL,
                action TEXT NOT NULL,
                success BOOLEAN NOT NULL,
                ip_hash TEXT,
                details TEXT,
                risk_level TEXT DEFAULT 'low',
                timestamp INTEGER NOT NULL
            )""",
        ]
        
        # Create indexes for performance
        index_queries = [
            "CREATE INDEX IF NOT EXISTS idx_user_properties_user_id ON user_properties(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_user_properties_key ON user_properties(key)",
            "CREATE INDEX IF NOT EXISTS idx_username_map_username ON username_map(username)",
            "CREATE INDEX IF NOT EXISTS idx_onchain_alerts_user_id ON onchain_alerts(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_onchain_alerts_active ON onchain_alerts(active)",
            "CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_user_sessions_active ON user_sessions(active)",
            "CREATE INDEX IF NOT EXISTS idx_command_analytics_user_id ON command_analytics(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_command_analytics_command ON command_analytics(command)",
            "CREATE INDEX IF NOT EXISTS idx_command_analytics_timestamp ON command_analytics(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_security_audit_user_id ON security_audit(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_security_audit_timestamp ON security_audit(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_security_audit_risk_level ON security_audit(risk_level)",
        ]
        
        try:
            with self.pool.get_connection() as conn:
                # Create tables
                for query in schema_queries:
                    conn.execute(query)
                
                # Create indexes
                for query in index_queries:
                    conn.execute(query)
                
                conn.commit()
                logger.info("Database schema initialized successfully")
                
        except Exception as e:
            logger.error(f"Failed to initialize database schema: {e}")
            raise
    
    def execute_query(self, query: str, params: tuple = (), fetch: str = None) -> QueryResult:
        """
        Execute a database query with performance tracking and error handling.
        
        Args:
            query: SQL query string
            params: Query parameters
            fetch: 'one', 'all', or None for no fetch
        """
        start_time = time.time()
        
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.execute(query, params)
                
                if fetch == 'one':
                    data = cursor.fetchone()
                    data = dict(data) if data else None
                elif fetch == 'all':
                    data = cursor.fetchall()
                    data = [dict(row) for row in data] if data else []
                else:
                    data = None
                
                conn.commit()
                
                execution_time = time.time() - start_time
                
                return QueryResult(
                    data=data,
                    execution_time=execution_time,
                    rows_affected=cursor.rowcount,
                    success=True
                )
                
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Database query failed: {e}")
            
            return QueryResult(
                data=None,
                execution_time=execution_time,
                success=False,
                error=str(e)
            )
    
    def set_user_property(self, user_id: int, key: str, value: str, encrypted: bool = False) -> bool:
        """Set user property with optional encryption"""
        try:
            final_value = value
            if encrypted and self.fernet:
                final_value = self.fernet.encrypt(value.encode()).decode()
            elif encrypted and not self.fernet:
                logger.error(f"Cannot encrypt property '{key}': Encryption not available")
                return False
            
            query = """
                INSERT OR REPLACE INTO user_properties 
                (user_id, key, value, encrypted, updated_at) 
                VALUES (?, ?, ?, ?, strftime('%s', 'now'))
            """
            
            result = self.execute_query(query, (user_id, key, final_value, encrypted))
            
            # Clear cache for this user
            self._clear_user_cache(user_id)
            
            return result.success
            
        except Exception as e:
            logger.error(f"Failed to set user property: {e}")
            return False
    
    def get_user_property(self, user_id: int, key: str, default: Any = None) -> Any:
        """Get user property with caching and decryption"""
        cache_key = f"user_prop_{user_id}_{key}"
        
        # Check cache first
        if self._is_cache_valid(cache_key):
            return self._query_cache[cache_key]
        
        try:
            query = "SELECT value, encrypted FROM user_properties WHERE user_id = ? AND key = ?"
            result = self.execute_query(query, (user_id, key), fetch='one')
            
            if not result.success or not result.data:
                return default
            
            value = result.data['value']
            encrypted = result.data['encrypted']
            
            # Decrypt if necessary
            if encrypted and self.fernet:
                try:
                    value = self.fernet.decrypt(value.encode()).decode()
                except Exception as e:
                    logger.error(f"Failed to decrypt property '{key}' for user {user_id}: {e}")
                    return default
            
            # Cache the result
            self._cache_result(cache_key, value)
            
            return value
            
        except Exception as e:
            logger.error(f"Failed to get user property: {e}")
            return default
    
    def get_user_properties(self, user_id: int) -> Dict[str, Any]:
        """Get all properties for a user"""
        try:
            query = "SELECT key, value, encrypted FROM user_properties WHERE user_id = ?"
            result = self.execute_query(query, (user_id,), fetch='all')
            
            if not result.success:
                return {}
            
            properties = {}
            for row in result.data:
                key = row['key']
                value = row['value']
                encrypted = row['encrypted']
                
                # Decrypt if necessary
                if encrypted and self.fernet:
                    try:
                        value = self.fernet.decrypt(value.encode()).decode()
                    except Exception as e:
                        logger.error(f"Failed to decrypt property '{key}' for user {user_id}: {e}")
                        continue
                
                properties[key] = value
            
            return properties
            
        except Exception as e:
            logger.error(f"Failed to get user properties: {e}")
            return {}
    
    def add_alert(self, alert_id: str, user_id: int, chat_id: int, 
                  alert_type: str, params: Dict[str, Any]) -> bool:
        """Add a new alert with enhanced tracking"""
        try:
            query = """
                INSERT INTO onchain_alerts 
                (alert_id, user_id, chat_id, alert_type, params, created_at) 
                VALUES (?, ?, ?, ?, ?, strftime('%s', 'now'))
            """
            
            result = self.execute_query(
                query, 
                (alert_id, user_id, chat_id, alert_type, json.dumps(params))
            )
            
            return result.success
            
        except Exception as e:
            logger.error(f"Failed to add alert: {e}")
            return False
    
    def get_user_alerts(self, user_id: int, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get alerts for a user with filtering"""
        try:
            query = """
                SELECT alert_id, chat_id, alert_type, params, active, 
                       triggered_count, last_triggered, created_at
                FROM onchain_alerts 
                WHERE user_id = ?
            """
            params = [user_id]
            
            if active_only:
                query += " AND active = TRUE"
            
            query += " ORDER BY created_at DESC"
            
            result = self.execute_query(query, tuple(params), fetch='all')
            
            if not result.success:
                return []
            
            # Parse JSON params
            alerts = []
            for row in result.data:
                alert = dict(row)
                try:
                    alert['params'] = json.loads(alert['params'])
                except:
                    alert['params'] = {}
                alerts.append(alert)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Failed to get user alerts: {e}")
            return []
    
    def count_user_alerts(self, user_id: int, active_only: bool = True) -> int:
        """Count alerts for a user"""
        try:
            query = "SELECT COUNT(*) as count FROM onchain_alerts WHERE user_id = ?"
            params = [user_id]
            
            if active_only:
                query += " AND active = TRUE"
            
            result = self.execute_query(query, tuple(params), fetch='one')
            
            if result.success and result.data:
                return result.data['count']
            
            return 0
            
        except Exception as e:
            logger.error(f"Failed to count user alerts: {e}")
            return 0
    
    def log_command_analytics(self, user_id: int, command: str, execution_time: float, 
                            success: bool, error_type: Optional[str] = None):
        """Log command execution for analytics"""
        try:
            query = """
                INSERT INTO command_analytics 
                (user_id, command, execution_time, success, error_type, timestamp)
                VALUES (?, ?, ?, ?, ?, strftime('%s', 'now'))
            """
            
            self.execute_query(query, (user_id, command, execution_time, success, error_type))
            
        except Exception as e:
            logger.error(f"Failed to log command analytics: {e}")
    
    def get_analytics_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get analytics summary for the specified time period"""
        try:
            cutoff_time = int(time.time()) - (hours * 3600)
            
            # Total commands
            query1 = "SELECT COUNT(*) as total FROM command_analytics WHERE timestamp > ?"
            result1 = self.execute_query(query1, (cutoff_time,), fetch='one')
            total_commands = result1.data['total'] if result1.success else 0
            
            # Success rate
            query2 = "SELECT COUNT(*) as successful FROM command_analytics WHERE timestamp > ? AND success = TRUE"
            result2 = self.execute_query(query2, (cutoff_time,), fetch='one')
            successful_commands = result2.data['successful'] if result2.success else 0
            
            # Top commands
            query3 = """
                SELECT command, COUNT(*) as count 
                FROM command_analytics 
                WHERE timestamp > ? 
                GROUP BY command 
                ORDER BY count DESC 
                LIMIT 10
            """
            result3 = self.execute_query(query3, (cutoff_time,), fetch='all')
            top_commands = result3.data if result3.success else []
            
            # Average execution time
            query4 = "SELECT AVG(execution_time) as avg_time FROM command_analytics WHERE timestamp > ?"
            result4 = self.execute_query(query4, (cutoff_time,), fetch='one')
            avg_time = result4.data['avg_time'] if result4.success else 0
            
            return {
                'total_commands': total_commands,
                'successful_commands': successful_commands,
                'success_rate': (successful_commands / total_commands * 100) if total_commands > 0 else 0,
                'top_commands': top_commands,
                'avg_execution_time': avg_time or 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get analytics summary: {e}")
            return {}
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self._query_cache:
            return False
        
        if cache_key not in self._cache_ttl:
            return False
        
        return time.time() < self._cache_ttl[cache_key]
    
    def _cache_result(self, cache_key: str, data: Any):
        """Cache query result with TTL"""
        self._query_cache[cache_key] = data
        self._cache_ttl[cache_key] = time.time() + self._cache_timeout
    
    def _clear_user_cache(self, user_id: int):
        """Clear cache entries for a specific user"""
        keys_to_remove = [key for key in self._query_cache.keys() if f"user_prop_{user_id}_" in key]
        for key in keys_to_remove:
            self._query_cache.pop(key, None)
            self._cache_ttl.pop(key, None)
    
    def cleanup_old_data(self, days: int = 30):
        """Clean up old analytics and audit data"""
        try:
            cutoff_time = int(time.time()) - (days * 24 * 3600)
            
            # Clean old analytics
            query1 = "DELETE FROM command_analytics WHERE timestamp < ?"
            result1 = self.execute_query(query1, (cutoff_time,))
            
            # Clean old audit logs
            query2 = "DELETE FROM security_audit WHERE timestamp < ?"
            result2 = self.execute_query(query2, (cutoff_time,))
            
            # Clean expired sessions
            query3 = "DELETE FROM user_sessions WHERE expires_at < strftime('%s', 'now')"
            result3 = self.execute_query(query3)
            
            logger.info(f"Cleaned up old data: {result1.rows_affected + result2.rows_affected + result3.rows_affected} rows removed")
            
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
    
    def close(self):
        """Close database connections"""
        self.pool.close_all()

# Global enhanced database instance
enhanced_db = EnhancedDatabase()

# Convenience wrapper functions for backward compatibility
def get_user_property(user_id: int, key: str, default: Any = None) -> Any:
    """Get user property wrapper function"""
    return enhanced_db.get_user_property(user_id, key, default)

def set_user_property(user_id: int, key: str, value: str, encrypted: bool = False) -> bool:
    """Set user property wrapper function"""
    return enhanced_db.set_user_property(user_id, key, value, encrypted)

def get_user_properties(user_id: int) -> Dict[str, Any]:
    """Get all user properties wrapper function"""
    return enhanced_db.get_user_properties(user_id)

def add_alert(alert_id: str, user_id: int, chat_id: int, alert_type: str, 
              conditions: Dict[str, Any], message_template: str, 
              is_active: bool = True) -> bool:
    """Add alert wrapper function"""
    return enhanced_db.add_alert(alert_id, user_id, chat_id, alert_type, 
                                conditions, message_template, is_active)

def get_user_alerts(user_id: int, active_only: bool = True) -> List[Dict[str, Any]]:
    """Get user alerts wrapper function"""
    return enhanced_db.get_user_alerts(user_id, active_only)

def log_command_analytics(user_id: int, command: str, execution_time: float,
                         success: bool = True, error_message: str = None) -> bool:
    """Log command analytics wrapper function"""
    return enhanced_db.log_command_analytics(user_id, command, execution_time, 
                                           success, error_message)
